from __future__ import annotations

from typing import cast

from aqt import gui_hooks
from aqt.browser import Browser
from aqt.qt import QAction, qconnect

from .gui.fill import FillDialog
from .session import get_db


def on_browser_action(browser: Browser) -> None:
    FillDialog(browser, get_db(), cast(list, browser.selected_notes())).show()


def add_browser_action(browser: Browser) -> None:
    action = QAction("InContext: Add sentences", browser)
    qconnect(action.triggered, lambda: on_browser_action(browser))
    browser.form.menu_Notes.addAction(action)


def init_hooks() -> None:
    gui_hooks.browser_menus_did_init.append(add_browser_action)
