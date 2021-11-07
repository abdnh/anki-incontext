from anki import hooks
from anki.template import TemplateRenderContext
from aqt.qt import *
from aqt import mw

from .sentences import get_sentence
from .incontext_dialog import InContextDialog


def incontext_filter(
    field_text: str,
    field_name: str,
    filter_name: str,
    ctx: TemplateRenderContext,
) -> str:
    if not filter_name.lower().startswith("incontext"):
        return field_text

    return get_sentence(field_text)


def open_dialog():
    dialog = InContextDialog(mw)
    dialog.exec_()


hooks.field_filter.append(incontext_filter)

action = QAction(mw)
action.setText("InContext")
mw.form.menuTools.addAction(action)
action.triggered.connect(open_dialog)
