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
        providers: list[str] | None = None,
        auto_search: bool = False,
    ):
        self._kwargs: dict[str, Any] = {
            "auto": auto_search,
        }
        if word:
            self._kwargs["word"] = word
        if language:
            self._kwargs["language"] = language
        if providers is not None:
            self._kwargs["providers"] = ",".join(providers)

        super().__init__(path="browse", parent=parent, subtitle="Browse Sentences")

    def get_query_params(self) -> dict[str, Any]:
        return self._kwargs
