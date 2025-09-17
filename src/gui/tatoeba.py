from aqt.qt import QWidget

from .sveltekit_web import SveltekitWebDialog


class TatoebaDialog(SveltekitWebDialog):
    def __init__(self, parent: QWidget):
        super().__init__(
            path="tatoeba", parent=parent, subtitle="Download Tatoeba Databases"
        )
