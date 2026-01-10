from __future__ import annotations

import functools
from typing import Callable

from aqt import Qt, gui_hooks, mw
from aqt.main import MainWindowState

from .config import config
from .gui.browse import BrowseDialog


def on_state_shortcuts_will_change(state: MainWindowState, shortcuts: list[tuple[str, Callable]]) -> None:
    if state != "review":
        return

    def search(language: str, providers: list[str]) -> None:
        word = mw.web.selectedText()
        if dialog := BrowseDialog.get_active_instance():
            if dialog.windowState() & Qt.WindowState.WindowMinimized:
                dialog.setWindowState(dialog.windowState() & ~Qt.WindowState.WindowMinimized)
            dialog.activateWindow()
            dialog.raise_()
            dialog.query(word, language, providers)
        else:
            BrowseDialog(
                word=word,
                language=language,
                providers=providers,
                auto_search=True,
            ).show()

    for shortcut in config["search_shortcuts"]:
        shortcuts.append(
            (
                shortcut["shortcut"],
                functools.partial(
                    search,
                    language=shortcut["language"],
                    providers=shortcut["providers"],
                ),
            )
        )


def init_hooks() -> None:
    gui_hooks.state_shortcuts_will_change.append(on_state_shortcuts_will_change)
