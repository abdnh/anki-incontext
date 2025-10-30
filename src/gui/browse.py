from __future__ import annotations

from typing import Any

from aqt.qt import QWidget

from .sveltekit_web import SveltekitWebDialog


class BrowseDialog(SveltekitWebDialog):
    key = "browse"

    def __init__(
        self,
        parent: QWidget | None = None,
        word: str = "",
        language: str = "",
        providers: list[str] = [],
        auto_search: bool = False,
    ):
        self._kwargs = {
            "word": word,
            "language": language,
            "providers": ",".join(providers),
            "auto": auto_search,
        }
        super().__init__(path="browse", parent=parent, subtitle="Browse Sentences")

    def get_query_params(self) -> dict[str, Any]:
        return self._kwargs
