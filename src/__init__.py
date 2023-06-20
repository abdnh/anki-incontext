from __future__ import annotations

import html
import json
import sys
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Any, cast

from anki import hooks
from anki.cards import Card
from anki.hooks import wrap
from anki.template import TemplateRenderContext
from aqt import gui_hooks, mw
from aqt.addons import AddonManager
from aqt.browser import Browser
from aqt.clayout import CardLayout
from aqt.qt import *
from aqt.reviewer import Reviewer
from aqt.webview import AnkiWebView, WebContent

try:
    from aqt.browser.previewer import Previewer
except ImportError:
    from aqt.previewer import Previewer  # type: ignore

from . import consts
from .errors import InContextError

sys.path.append(str(consts.VENDOR_DIR))

# pylint: disable=wrong-import-position
from .db import SentenceDB
from .gui.fill import FillDialog
from .gui.main import InContextDialog
from .providers import get_provider, get_sentences, init_providers

WEB_BASE = f"/_addons/{mw.addonManager.addonFromModule(__name__)}/web/"


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
        # pylint: disable=protected-access
        return CardContext(window.card(), window._web)
    return CardContext(mw.reviewer.card, mw.reviewer.web)


def get_formatted_sentence(text: str, lang: str, provider: str) -> str:
    try:
        sentences = get_sentences(word=text, language=lang, provider=provider, limit=1)
        sentence = sentences[0] if sentences else None
        provider_obj = get_provider(sentence.provider) if sentence else None
        source = (
            f'<br><br>Source: <a href="{provider_obj.get_source(text, lang)}">{provider_obj.human_name}</a>'
            if provider_obj
            else ""
        )
        ret = f"{sentence.text if sentence else ''} {source}"
    except InContextError as exc:
        ret = f"<div style='color: red'>InContext error: {html.escape(str(exc))}</div>"
    return ret


def incontext_filter(
    field_text: str,
    field_name: str,
    filter_name: str,
    ctx: TemplateRenderContext,
) -> str:
    if not filter_name.lower().startswith("incontext"):
        return field_text

    ctx.extra_state.setdefault("incontext_id", 0)
    filter_id = ctx.extra_state["incontext_id"]

    options = dict(map(lambda o: o.split("="), filter_name.split()[1:]))
    lang = options.get("lang", "en")
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
                """(() => {
                    const inContextIntervalID = setTimeout(() => {
                        const inContextSentenceElement = document.getElementById('incontext-sentence-%(filter_id)d');
                        if(inContextSentenceElement) {
                            clearInterval(inContextIntervalID);
                            const result = %(result)s;
                            globalThis.inContextResults.push(result);
                            inContextSentenceElement.innerHTML = result;
                        }
                    }, 100);
                })();"""
                % dict(result=json.dumps(result), filter_id=filter_id)
            )

    mw.taskman.run_in_background(task, on_done)
    ctx.extra_state["incontext_id"] += 1
    return """
    <div class='incontext-sentence' id='incontext-sentence-%(filter_id)d' data-query='%(field_text)s' data-lang='%(lang)s' data-provider='%(provider)s'>InContext: fetching sentence...</div>
    <img src="%(refresh_icon)s" class="incontext-refresh-button" onclick="InContextRefreshSentence(%(filter_id)d)">
    <script>
        if(globalThis.inContextResults[%(filter_id)d]) {
            document.getElementById('incontext-sentence-%(filter_id)d').innerHTML = globalThis.inContextResults[%(filter_id)d];
        }
    </script>
    """ % dict(
        filter_id=filter_id,
        refresh_icon=f"{WEB_BASE}arrow-clockwise.svg",
        field_text=html.escape(field_text),
        lang=html.escape(lang),
        provider=html.escape(provider) if provider else "",
    )


def on_card_will_show(text: str, card: Card, kind: str) -> str:
    if kind.endswith("Question"):
        text = "<script>globalThis.inContextResults = [];</script>" + text
    return text


def on_webview_will_set_content(web_content: WebContent, context: Any | None) -> None:
    if not isinstance(context, (Reviewer, Previewer, CardLayout)):
        return
    web_content.css.append(f"{WEB_BASE}incontext.css")
    web_content.js.append(f"{WEB_BASE}incontext.js")


def on_webview_did_receive_js_message(
    handled: tuple[bool, Any], message: str, context: Any
) -> tuple[bool, Any]:
    if not message.startswith("incontext:"):
        return handled
    _, subcmd, data = message.split(":", maxsplit=2)
    if subcmd == "refresh":
        options = json.loads(data)

        def task() -> str:
            return get_formatted_sentence(
                options["query"], options["lang"], options["provider"]
            )

        def on_done(fut: Future) -> None:
            result = fut.result()
            card_context = get_active_card_context()
            if card_context.card and card_context.web:
                card_context.web.eval(
                    """(() => {
                        const result = %(result)s;
                        globalThis.inContextResults[%(filter_id)d] = result;
                        document.getElementById('incontext-sentence-%(filter_id)d').innerHTML = result;
                    })();"""
                    % dict(result=json.dumps(result), filter_id=options["id"])
                )

        mw.taskman.run_in_background(task, on_done)

    return True, None


dialog: InContextDialog | None = None


def on_finished() -> None:
    global dialog
    dialog = None


def open_dialog() -> None:
    global dialog
    if not dialog:
        dialog = InContextDialog(mw, sentences_db)
        qconnect(dialog.finished, on_finished)
        dialog.show()
    else:
        if dialog.windowState() & Qt.WindowState.WindowMinimized:
            dialog.setWindowState(
                dialog.windowState() & ~Qt.WindowState.WindowMinimized
            )
        dialog.activateWindow()
        dialog.raise_()


sentences_db: SentenceDB | None = None


def init_db() -> None:
    global sentences_db
    sentences_db = SentenceDB()
    init_providers(sentences_db)


def on_browser_action(browser: Browser) -> None:
    FillDialog(browser, mw, sentences_db, cast(list, browser.selected_notes())).exec()


def add_browser_action(browser: Browser) -> None:
    action = QAction("InContext: Add sentences", browser)
    qconnect(action.triggered, lambda: on_browser_action(browser))
    browser.form.menu_Notes.addAction(action)


def on_addon_manager_will_install_addon(
    manager: AddonManager, module: str, *args: Any, **kwargs: Any
) -> None:
    if module == manager.addonFromModule(__name__):
        sentences_db.close()


def on_addon_manager_did_install_addon(
    manager: AddonManager, module: str, *args: Any, **kwargs: Any
) -> None:
    if module == manager.addonFromModule(__name__):
        init_db()
        if dialog is not None:
            dialog.sentences_db = sentences_db


hooks.field_filter.append(incontext_filter)
gui_hooks.card_will_show.append(on_card_will_show)
gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
gui_hooks.webview_did_receive_js_message.append(on_webview_did_receive_js_message)
gui_hooks.browser_menus_did_init.append(add_browser_action)
if hasattr(gui_hooks, "addon_manager_will_install_addon"):
    gui_hooks.addon_manager_will_install_addon.append(
        on_addon_manager_will_install_addon
    )
else:
    AddonManager._install = wrap(
        AddonManager._install, on_addon_manager_will_install_addon, "before"
    )

if hasattr(gui_hooks, "addon_manager_did_install_addon"):
    gui_hooks.addon_manager_did_install_addon.append(on_addon_manager_did_install_addon)
else:
    AddonManager._install = wrap(
        AddonManager._install, on_addon_manager_did_install_addon, "after"
    )

mw.addonManager.setWebExports(__name__, "web/.*")
action = QAction("InContext", mw)
mw.form.menuTools.addAction(action)
init_db()
qconnect(action.triggered, open_dialog)
