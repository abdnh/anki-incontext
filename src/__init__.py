from anki import hooks
from anki.template import TemplateRenderContext
from aqt import mw
from aqt.qt import *

from .db import SentenceDB
from .incontext_dialog import InContextDialog
from .providers import get_sentence, init_providers


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
    sentence = get_sentence(word=field_text, language=lang)
    return sentence.text if sentence else ""


def open_dialog() -> None:
    dialog = InContextDialog(mw, sentences_db)
    dialog.exec()


hooks.field_filter.append(incontext_filter)

if mw:
    action = QAction(mw)
    action.setText("InContext")
    mw.form.menuTools.addAction(action)
    sentences_db = SentenceDB()
    init_providers(sentences_db)
    qconnect(action.triggered, open_dialog)
