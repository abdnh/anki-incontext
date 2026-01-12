from aqt import QMenu, mw
from aqt.qt import QAction, qconnect

from .gui.browse import BrowseDialog
from .gui.help import HelpDialog
from .gui.settings import SettingsDialog
from .gui.tatoeba import TatoebaDialog


def open_tatoeba_dialog() -> None:
    TatoebaDialog().show()


def open_browse_dialog() -> None:
    BrowseDialog().show()


def open_settings_dialog() -> None:
    SettingsDialog().show()


def open_help_dialog() -> None:
    HelpDialog().show()


def init() -> None:
    menu = QMenu("InContext", mw)
    tatoeba_action = QAction("Download Tatoeba sentences", mw)
    qconnect(tatoeba_action.triggered, open_tatoeba_dialog)
    menu.addAction(tatoeba_action)
    browse_action = QAction("Browse sentences", mw)
    qconnect(browse_action.triggered, open_browse_dialog)
    menu.addAction(browse_action)
    settings_action = QAction("Settings", mw)
    qconnect(settings_action.triggered, open_settings_dialog)
    menu.addAction(settings_action)
    help_action = QAction("Help", mw)
    qconnect(help_action.triggered, open_help_dialog)
    menu.addAction(help_action)
    mw.form.menuTools.addMenu(menu)
