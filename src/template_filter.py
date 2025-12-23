from __future__ import annotations

import html
import json
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Any

from anki import hooks
from anki.cards import Card
from anki.template import TemplateRenderContext
from aqt import gui_hooks, mw
from aqt.clayout import CardLayout
from aqt.qt import QApplication
from aqt.reviewer import Reviewer
from aqt.webview import AnkiWebView, WebContent

try:
    from aqt.browser.previewer import Previewer
except ImportError:
    from aqt.previewer import Previewer  # type: ignore

from .exceptions import InContextError
from .gui.operations import run_task_in_background
from .providers import get_provider, get_sentences

WEB_BASE = f"/_addons/{mw.addonManager.addonFromModule(__name__)}/web"


@dataclass
class CardContext:
    card: Card | None = None
    web: AnkiWebView | None = None


def get_active_card_context() -> CardContext:
    dialog = QApplication.activeModalWidget()
    if isinstance(dialog, CardLayout):
        return CardContext(dialog.rendered_card, dialog.preview_web)
    window = QApplication.activeWindow()
    if isinstance(window, Previewer):
        return CardContext(window.card(), window._web)
    return CardContext(mw.reviewer.card, mw.reviewer.web)


def get_formatted_sentence(text: str, lang: str | None, provider: str | None) -> str:
    try:
        sentences = get_sentences(
            word=text,
            language=lang,
            providers=[provider] if provider else None,
            limit=1,
        )
        sentence = sentences[0] if sentences else None
        provider_obj = get_provider(sentence.provider) if sentence else None
        if not lang and provider_obj:
            lang = provider_obj.supported_languages[0]
        source = (
            f'<br><br>Source: <a href="{provider_obj.get_source(text, lang)}">'
            f"{provider_obj.human_name}</a>"
            if provider_obj
            else ""
        )
        ret = f"{sentence.text if sentence else ''} {source}"
    except InContextError as exc:
        ret = f"<div style='color: red'>InContext error: {html.escape(str(exc))}</div>"
    return ret


incontext_id = 0


def incontext_filter(
    field_text: str,
    field_name: str,
    filter_name: str,
    ctx: TemplateRenderContext,
) -> str:
    if not filter_name.lower().startswith("incontext"):
        return field_text

    global incontext_id
    filter_id = incontext_id

    options = dict(map(lambda o: o.split("="), filter_name.split()[1:]))
    lang = options.get("lang", None)
    # TODO: support multiple comma-separated providers
    provider = options.get("provider", None)

    def task() -> str:
        return get_formatted_sentence(field_text, lang, provider)

    def on_done(fut: Future) -> None:
        result = fut.result()
        card_context = get_active_card_context()
        if (
            card_context.card
            and card_context.web
            and card_context.card.id == ctx.card().id
        ):
            card_context.web.eval(
                f"incontext.saveAndRenderSentence({filter_id}, {json.dumps(result)})"
            )

    run_task_in_background(task, on_done, uses_collection=False)
    incontext_id += 1

    refresh_icon = f"{WEB_BASE}/arrow-clockwise.svg"
    return f"""
    <div
      class='incontext-sentence'
      id='incontext-sentence-{filter_id}'
      data-query='{html.escape(field_text)}'
      data-lang='{html.escape(lang) if lang else ""}'
      data-provider='{html.escape(provider) if provider else ""}'>
        InContext: fetching sentence...
    </div>
    <img
      src="{refresh_icon}"
      class="incontext-refresh-button incontext-loading"
      onclick="incontext.refreshSentence({filter_id})"
    >
    <script>
        incontext.renderSentence({filter_id});
    </script>
    """


def on_card_will_show(text: str, card: Card, kind: str) -> str:
    if kind.endswith("Question"):
        text = "<script>globalThis.inContextResults = [];</script>" + text
    return text


def on_webview_will_set_content(web_content: WebContent, context: Any | None) -> None:
    if not isinstance(context, (Reviewer, Previewer, CardLayout)):
        return
    web_content.css.append(f"{WEB_BASE}/incontext.css")
    web_content.js.append(f"{WEB_BASE}/incontext.js")


def on_webview_did_receive_js_message(
    handled: tuple[bool, Any], message: str, context: Any
) -> tuple[bool, Any]:
    if not message.startswith("incontext:"):
        return handled
    _, subcmd, data = message.split(":", maxsplit=2)
    if subcmd == "refresh":
        options = json.loads(data)
        filter_id = options["id"]
        card_context = get_active_card_context()

        def task() -> str:
            return get_formatted_sentence(
                options["query"], options["lang"], options["provider"]
            )

        def on_done(fut: Future) -> None:
            sentence = fut.result()
            if card_context.card and card_context.web:
                card_context.web.eval(
                    f"""
                    incontext.addSentence({filter_id}, {json.dumps(sentence)});
                    incontext.renderSentence({filter_id});
                    """
                )

        card_context.web.eval(f"incontext.setLoading({filter_id});")
        run_task_in_background(task, on_done, uses_collection=False)

    return True, None


def init_hooks() -> None:
    hooks.field_filter.append(incontext_filter)
    gui_hooks.card_will_show.append(on_card_will_show)
    gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
    gui_hooks.webview_did_receive_js_message.append(on_webview_did_receive_js_message)
    mw.addonManager.setWebExports(__name__, "web/.*")
