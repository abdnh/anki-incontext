from __future__ import annotations

from aqt.qt import QWidget

from .sveltekit_web import SveltekitWebDialog


class TatoebaDialog(SveltekitWebDialog):
    key = "tatoeba"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(path="tatoeba", parent=parent, subtitle="Download Tatoeba Databases")
