from __future__ import annotations

from aqt import mw
from aqt.qt import QWidget
from aqt.utils import tooltip

from ..backend.server import get_server
from ..config import config
from ..keys import js_key_to_qt
from ..proto.backend_pb2 import SaveSettingsRequest
from .sveltekit_web import SveltekitWebDialog


class SettingsDialog(SveltekitWebDialog):
    key = "settings"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(path="settings", parent=parent, subtitle="Settings")
        get_server().add_proto_handler_for_dialog(
            self,
            "ankiaddon.backend.BackendService",
            "SaveSettings",
            self._save_settings_request,
        )

    def _save_settings_request(self, data: bytes) -> bytes:
        request = SaveSettingsRequest.FromString(data)
        search_shortcuts = []
        for shortcut in request.search_shortcuts:
            search_shortcuts.append(
                {
                    "shortcut": js_key_to_qt(shortcut.keys),
                    "language": shortcut.language,
                    "providers": list(shortcut.selected_providers),
                }
            )
        config["search_shortcuts"] = search_shortcuts

        def on_main() -> None:
            self.close()
            tooltip("Settings saved", parent=mw)

        mw.taskman.run_on_main(on_main)

        return b""
