from aqt import QMenu, mw
from aqt.qt import QAction, qconnect

from .errors import upload_logs_and_notify_user
from .gui.browse import BrowseDialog
from .gui.help import HelpDialog
from .gui.languages import LanguagesDialog
from .gui.settings import SettingsDialog
from .gui.tatoeba import TatoebaDialog


def on_help() -> None:
    HelpDialog().show()


def on_upload_logs() -> None:
    upload_logs_and_notify_user(mw)


def open_tatoeba_dialog() -> None:
    TatoebaDialog().show()


def open_browse_dialog() -> None:
    BrowseDialog().show()


def open_settings_dialog() -> None:
    SettingsDialog().show()


def open_languages_dialog() -> None:
    LanguagesDialog().show()


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
    languages_action = QAction("Languages", mw)
    qconnect(languages_action.triggered, open_languages_dialog)
    menu.addAction(languages_action)
    menu.addAction("Upload logs", on_upload_logs)
    menu.addAction("Help", on_help)
    mw.form.menuTools.addMenu(menu)
