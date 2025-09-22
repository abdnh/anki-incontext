from aqt.qt import QWidget

from .sveltekit_web import SveltekitWebDialog


class BrowseDialog(SveltekitWebDialog):
    key = "browse"

    def __init__(self, parent: QWidget):
        super().__init__(path="browse", parent=parent, subtitle="Browse Sentences")
