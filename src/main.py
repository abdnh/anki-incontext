from __future__ import annotations

from .patches import patch_certifi

patch_certifi()

# ruff: noqa: E402
from . import browser, menu, session, shortcuts, template_filter, updates
from .backend.server import init_server
from .errors import setup_error_handler


def init() -> None:
    setup_error_handler()
    init_server()
    session.init_db()
    template_filter.init_hooks()
    updates.init_hooks()
    browser.init_hooks()
    shortcuts.init_hooks()
    menu.init()
