from __future__ import annotations

from aqt.qt import QWidget

from .sveltekit_web import SveltekitWebDialog


class LanguagesDialog(SveltekitWebDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(path="languages", parent=parent, subtitle="Languages")
