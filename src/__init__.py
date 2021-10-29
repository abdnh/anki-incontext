from anki import hooks
from anki.template import TemplateRenderContext

from .sentences import get_sentence


def incontext_filter(
    field_text: str,
    field_name: str,
    filter_name: str,
    ctx: TemplateRenderContext,
) -> str:
    if not filter_name.lower().startswith("incontext"):
        return field_text

    return get_sentence(field_text)


hooks.field_filter.append(incontext_filter)
