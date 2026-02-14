from __future__ import annotations

from .patches import patch_certifi

patch_certifi()

# ruff: noqa: E402
from . import browser, menu, session, shortcuts, template_filter
from .backend.server import init_server
from .config import config
from .consts import consts
from .errors import setup_error_handler
from .vendor.ankiutils import updates


def init() -> None:
    setup_error_handler()
    init_server()
    session.init_db()
    template_filter.init_hooks()
    updates.init_hooks(consts, config)
    browser.init_hooks()
    shortcuts.init_hooks()
    menu.init()
