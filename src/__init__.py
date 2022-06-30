from anki import hooks
from anki.template import TemplateRenderContext
from aqt import mw
from aqt.qt import *

from .incontext_dialog import InContextDialog
from .sentences import get_sentence


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

    return get_sentence(field_text, lang)


def open_dialog() -> None:
    dialog = InContextDialog(mw)
    dialog.exec()


hooks.field_filter.append(incontext_filter)

if mw:
    action = QAction(mw)
    action.setText("InContext")
    mw.form.menuTools.addAction(action)
    qconnect(action.triggered, open_dialog)
