from __future__ import annotations

from aqt.qt import QWidget

from .sveltekit_web import SveltekitWebDialog


class BrowseDialog(SveltekitWebDialog):
    key = "browse"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(path="browse", parent=parent, subtitle="Browse Sentences")
