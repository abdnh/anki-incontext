import sys

from anki import hooks
from anki.template import TemplateRenderContext
from aqt import mw
from aqt.qt import *

from . import consts

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
    # TODO: support multiple comma-separted providers
    provider = options.get("provider", None)
    sentence = get_sentence(word=field_text, language=lang, provider=provider)
    provider_obj = get_provider(sentence.provider) if sentence else None
    source = (
        f'<br><br>Source: <a href="{provider_obj.get_source(field_text, lang)}">{sentence.provider.title().replace("_", " ")}</a>'
        if provider_obj
        else ""
    )
    ret = f"{sentence.text if sentence else ''} {source}"
    return ret


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
