from __future__ import annotations

import json
from typing import Any

from aqt import mw
from aqt.qt import QClipboard, QWidget, qconnect, sip

from ..backend.server import get_server
from ..proto.backend_pb2 import GetClipboardTextResponse
from .sveltekit_web import SveltekitWebDialog


class BrowseDialog(SveltekitWebDialog):
    key = "browse"
    active_instance: BrowseDialog | None = None

    @classmethod
    def get_active_instance(cls) -> BrowseDialog | None:
        if cls.active_instance and not sip.isdeleted(cls.active_instance):
            return cls.active_instance
        return None

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
        self._clipboard_text = ""
        super().__init__(path="browse", parent=parent, subtitle="Browse Sentences")
        get_server().add_proto_handler_for_dialog(
            self,
            "ankiaddon.backend.BackendService",
            "GetClipboardText",
            self._get_clipboard_text,
        )
        qconnect(mw.app.clipboard().dataChanged, self._on_clipboard_data_changed)
        BrowseDialog.active_instance = self

    def get_query_params(self) -> dict[str, Any]:
        return {
            **super().get_query_params(),
            **self._kwargs,
        }

    def _on_clipboard_data_changed(self) -> None:
        self._clipboard_text = mw.app.clipboard().text(QClipboard.Mode.Clipboard)

    def _get_clipboard_text(self, data: bytes) -> bytes:
        response = GetClipboardTextResponse(text=self._clipboard_text)
        return response.SerializeToString()

    def query(self, word: str, language: str, providers: list[str]) -> None:
        payload = {
            "word": word,
            "language": language,
            "providers": providers,
        }
        self.web.eval(f"incontext.runQuery({json.dumps(payload)})")
