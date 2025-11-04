from typing import Any

from anki.hooks import wrap
from aqt import gui_hooks, mw
from aqt.addons import AddonManager, AddonsDialog

from .session import get_db, init_db


def on_addon_manager_will_install_addon(
    manager: AddonManager, module: str, *args: Any, **kwargs: Any
) -> None:
    if module == manager.addonFromModule(__name__):
        get_db().close()


def on_addon_manager_did_install_addon(
    manager: AddonManager, module: str, *args: Any, **kwargs: Any
) -> None:
    if module == manager.addonFromModule(__name__):
        init_db()


def on_addons_dialog_will_delete_addons(dialog: AddonsDialog, ids: list[str]) -> None:
    if mw.addonManager.addonFromModule(__name__) in ids:
        get_db().close()


def init_hooks() -> None:
    if hasattr(gui_hooks, "addon_manager_will_install_addon"):
        gui_hooks.addon_manager_will_install_addon.append(
            on_addon_manager_will_install_addon
        )
    else:
        AddonManager._install = wrap(  # type: ignore
            AddonManager._install, on_addon_manager_will_install_addon, "before"
        )

    if hasattr(gui_hooks, "addon_manager_did_install_addon"):
        gui_hooks.addon_manager_did_install_addon.append(
            on_addon_manager_did_install_addon
        )
    else:
        AddonManager._install = wrap(  # type: ignore
            AddonManager._install, on_addon_manager_did_install_addon, "after"
        )
    gui_hooks.addons_dialog_will_delete_addons.append(
        on_addons_dialog_will_delete_addons
    )
