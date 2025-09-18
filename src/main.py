from __future__ import annotations

from .patches import patch_certifi

patch_certifi()

# ruff: noqa: E402

import html
import json
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Any, cast

from anki import hooks
from anki.cards import Card
from anki.hooks import wrap
from anki.template import TemplateRenderContext
from aqt import QMenu, gui_hooks, mw
from aqt.addons import AddonManager, AddonsDialog
from aqt.browser import Browser
from aqt.clayout import CardLayout
from aqt.qt import QAction, QApplication, Qt, qconnect
from aqt.reviewer import Reviewer
from aqt.webview import AnkiWebView, WebContent

from .backend.server import init_server
from .errors import setup_error_handler

try:
    from aqt.browser.previewer import Previewer
except ImportError:
    from aqt.previewer import Previewer  # type: ignore

from .db import SentenceDB
from .exceptions import InContextError
from .gui.fill import FillDialog
from .gui.main import InContextDialog
from .gui.tatoeba import TatoebaDialog
from .providers import get_provider, get_sentences, init_providers

WEB_BASE = f"/_addons/{mw.addonManager.addonFromModule(__name__)}/web"


@dataclass
class CardContext:
    card: Card | None = None
    web: AnkiWebView | None = None


def get_active_card_context() -> CardContext:
    dialog = QApplication.activeModalWidget()
    if isinstance(dialog, CardLayout):
        return CardContext(dialog.rendered_card, dialog.preview_web)
    window = QApplication.activeWindow()
    if isinstance(window, Previewer):
        # pylint: disable=protected-access
        return CardContext(window.card(), window._web)
    return CardContext(mw.reviewer.card, mw.reviewer.web)


def get_formatted_sentence(text: str, lang: str | None, provider: str | None) -> str:
    try:
        sentences = get_sentences(word=text, language=lang, provider=provider, limit=1)
        sentence = sentences[0] if sentences else None
        provider_obj = get_provider(sentence.provider) if sentence else None
        if not lang and provider_obj:
            lang = provider_obj.supported_languages[0]
        source = (
            f'<br><br>Source: <a href="{provider_obj.get_source(text, lang)}">'
            f"{provider_obj.human_name}</a>"
            if provider_obj
            else ""
        )
        ret = f"{sentence.text if sentence else ''} {source}"
    except InContextError as exc:
        ret = f"<div style='color: red'>InContext error: {html.escape(str(exc))}</div>"
    return ret


def incontext_filter(
    field_text: str,
    field_name: str,
    filter_name: str,
    ctx: TemplateRenderContext,
) -> str:
    if not filter_name.lower().startswith("incontext"):
        return field_text

    ctx.extra_state.setdefault("incontext_id", 0)
    filter_id = ctx.extra_state["incontext_id"]

    options = dict(map(lambda o: o.split("="), filter_name.split()[1:]))
    lang = options.get("lang", None)
    # TODO: support multiple comma-separated providers
    provider = options.get("provider", None)

    def task() -> str:
        return get_formatted_sentence(field_text, lang, provider)

    def on_done(fut: Future) -> None:
        result = fut.result()
        card_context = get_active_card_context()
        if (
            card_context.card
            and card_context.web
            and card_context.card.id == ctx.card().id
        ):
            card_context.web.eval(
                f"incontext.saveAndRenderSentence({filter_id}, {json.dumps(result)})"
            )

    mw.taskman.run_in_background(task, on_done)
    ctx.extra_state["incontext_id"] += 1

    refresh_icon = f"{WEB_BASE}/arrow-clockwise.svg"
    return f"""
    <div
      class='incontext-sentence'
      id='incontext-sentence-{filter_id}'
      data-query='{html.escape(field_text)}'
      data-lang='{html.escape(lang) if lang else ""}'
      data-provider='{html.escape(provider) if provider else ""}'>
        InContext: fetching sentence...
    </div>
    <img
      src="{refresh_icon}"
      class="incontext-refresh-button incontext-loading"
      onclick="incontext.refreshSentence({filter_id})"
    >
    <script>
        incontext.renderSentence({filter_id});
    </script>
    """


def on_card_will_show(text: str, card: Card, kind: str) -> str:
    if kind.endswith("Question"):
        text = "<script>globalThis.inContextResults = [];</script>" + text
    return text


def on_webview_will_set_content(web_content: WebContent, context: Any | None) -> None:
    if not isinstance(context, (Reviewer, Previewer, CardLayout)):
        return
    web_content.css.append(f"{WEB_BASE}/incontext.css")
    web_content.js.append(f"{WEB_BASE}/incontext.js")


def on_webview_did_receive_js_message(
    handled: tuple[bool, Any], message: str, context: Any
) -> tuple[bool, Any]:
    if not message.startswith("incontext:"):
        return handled
    _, subcmd, data = message.split(":", maxsplit=2)
    if subcmd == "refresh":
        options = json.loads(data)
        filter_id = options["id"]
        card_context = get_active_card_context()

        def task() -> str:
            return get_formatted_sentence(
                options["query"], options["lang"], options["provider"]
            )

        def on_done(fut: Future) -> None:
            sentence = fut.result()
            if card_context.card and card_context.web:
                card_context.web.eval(
                    f"""
                    incontext.addSentence({filter_id}, {json.dumps(sentence)});
                    incontext.renderSentence({filter_id});
                    """
                )

        card_context.web.eval(f"incontext.setLoading({filter_id});")
        mw.taskman.run_in_background(task, on_done)

    return True, None


dialog: InContextDialog | None = None


def on_finished() -> None:
    global dialog
    dialog = None


def open_manage_dialog() -> None:
    global dialog
    if not dialog:
        dialog = InContextDialog(mw, sentences_db)
        qconnect(dialog.finished, on_finished)
        dialog.show()
    else:
        if dialog.windowState() & Qt.WindowState.WindowMinimized:
            dialog.setWindowState(
                dialog.windowState() & ~Qt.WindowState.WindowMinimized
            )
        dialog.activateWindow()
        dialog.raise_()


sentences_db: SentenceDB | None = None


def init_db() -> None:
    global sentences_db
    sentences_db = SentenceDB()
    init_providers(sentences_db)


def on_browser_action(browser: Browser) -> None:
    FillDialog(browser, sentences_db, cast(list, browser.selected_notes())).show()


def add_browser_action(browser: Browser) -> None:
    action = QAction("InContext: Add sentences", browser)
    qconnect(action.triggered, lambda: on_browser_action(browser))
    browser.form.menu_Notes.addAction(action)


def on_addon_manager_will_install_addon(
    manager: AddonManager, module: str, *args: Any, **kwargs: Any
) -> None:
    if module == manager.addonFromModule(__name__):
        sentences_db.close()


def on_addon_manager_did_install_addon(
    manager: AddonManager, module: str, *args: Any, **kwargs: Any
) -> None:
    if module == manager.addonFromModule(__name__):
        init_db()
        if dialog is not None:
            dialog.sentences_db = sentences_db


def on_addons_dialog_will_delete_addons(dialog: AddonsDialog, ids: list[str]) -> None:
    if mw.addonManager.addonFromModule(__name__) in ids:
        sentences_db.close()


def open_tatoeba_dialog() -> None:
    TatoebaDialog(mw).show()


def add_menu() -> None:
    menu = QMenu("InContext", mw)
    manage_action = QAction("Manage sentences", mw)
    qconnect(manage_action.triggered, open_manage_dialog)
    menu.addAction(manage_action)
    tatoeba_action = QAction("Download Tatoeba sentences", mw)
    qconnect(tatoeba_action.triggered, open_tatoeba_dialog)
    menu.addAction(tatoeba_action)
    mw.form.menuTools.addMenu(menu)


def init() -> None:
    setup_error_handler()
    init_server()
    hooks.field_filter.append(incontext_filter)
    gui_hooks.card_will_show.append(on_card_will_show)
    gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
    gui_hooks.webview_did_receive_js_message.append(on_webview_did_receive_js_message)
    gui_hooks.browser_menus_did_init.append(add_browser_action)
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
    mw.addonManager.setWebExports(__name__, "web/.*")
    init_db()
    add_menu()
