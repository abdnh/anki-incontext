from __future__ import annotations

import html
import json
import sys
from concurrent.futures import Future
from dataclasses import dataclass

from anki import hooks
from anki.cards import Card
from anki.template import TemplateRenderContext
from aqt import gui_hooks, mw
from aqt.browser.previewer import Previewer
from aqt.clayout import CardLayout
from aqt.qt import *
from aqt.webview import AnkiWebView

from . import consts
from .errors import InContextError

sys.path.append(str(consts.VENDOR_DIR))

# pylint: disable=wrong-import-position
from .db import SentenceDB
from .incontext_dialog import InContextDialog
from .providers import get_provider, get_sentence, init_providers


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
        try:
            sentence = get_sentence(word=field_text, language=lang, provider=provider)
            provider_obj = get_provider(sentence.provider) if sentence else None
            source = (
                f'<br><br>Source: <a href="{provider_obj.get_source(field_text, lang)}">{provider_obj.human_name}</a>'
                if provider_obj
                else ""
            )
            ret = f"{sentence.text if sentence else ''} {source}"
        except InContextError as exc:
            ret = f"<div style='color: red'>InContext error: {html.escape(str(exc))}</div>"
        return ret

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
                    const result = %(result)s;
                    globalThis.inContextResults.push(result);
                    document.getElementById('incontext-sentence-%(filter_id)d').innerHTML = result;
                })();"""
                % dict(result=json.dumps(result), filter_id=filter_id)
            )

    mw.taskman.run_in_background(task, on_done)
    ctx.extra_state["incontext_id"] += 1
    return """
    <div class='incontext-sentence' id='incontext-sentence-%(filter_id)d'>InContext: fetching sentence...</div>
    <script>
        if(globalThis.inContextResults[%(filter_id)d]) {
            document.getElementById('incontext-sentence-%(filter_id)d').innerHTML = globalThis.inContextResults[%(filter_id)d];
        }
    </script>
    """ % dict(
        filter_id=filter_id
    )


def on_card_will_show(text: str, card: Card, kind: str) -> str:
    if kind.endswith("Question"):
        text = "<script>globalThis.inContextResults = [];</script>" + text
    return text


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


hooks.field_filter.append(incontext_filter)
gui_hooks.card_will_show.append(on_card_will_show)
action = QAction("InContext", mw)
mw.form.menuTools.addAction(action)
sentences_db = SentenceDB()
init_providers(sentences_db)
qconnect(action.triggered, open_dialog)
