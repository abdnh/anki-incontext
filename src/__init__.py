from __future__ import annotations

import sys

from anki import hooks
from anki.template import TemplateRenderContext
from aqt import mw
from aqt.qt import *

from . import consts
from .errors import InContextError

sys.path.append(str(consts.VENDOR_DIR))

# pylint: disable=wrong-import-position
from .db import SentenceDB
from .incontext_dialog import InContextDialog
from .providers import get_provider, get_sentence, init_providers


def incontext_filter(
    field_text: str,
    field_name: str,
    filter_name: str,
    ctx: TemplateRenderContext,
) -> str:
    if not filter_name.lower().startswith("incontext"):
        return field_text

    options = dict(map(lambda o: o.split("="), filter_name.split()[1:]))
    lang = options.get("lang", "en")
    # TODO: support multiple comma-separated providers
    provider = options.get("provider", None)
    try:
        sentence = get_sentence(word=field_text, language=lang, provider=provider)
        provider_obj = get_provider(sentence.provider) if sentence else None
        source = (
            f'<br><br>Source: <a href="{provider_obj.get_source(field_text, lang)}">{provider_obj.human_name}</a>'
            if provider_obj
            else ""
        )
        return f"{sentence.text if sentence else ''} {source}"
    except InContextError as exc:
        return f"<div style='color: red'>InContext error: {str(exc)}</div>"


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

if mw:
    action = QAction(mw)
    action.setText("InContext")
    mw.form.menuTools.addAction(action)
    sentences_db = SentenceDB()
    init_providers(sentences_db)
    qconnect(action.triggered, open_dialog)
