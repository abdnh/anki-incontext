from __future__ import annotations

import json
from collections.abc import Iterable

from anki.collection import Collection
from anki.notes import NoteId
from anki.utils import ids2str
from aqt import mw
from aqt.main import AnkiQt

from ..config import config
from ..consts import consts
from ..gui.operations import AddonQueryOp
from ..keys import qt_key_to_js
from ..log import logger
from ..proto.backend_pb2 import (
    DownloadTatoebaSentencesRequest,
    GetDefaultFillFieldsRequest,
    GetDefaultFillFieldsResponse,
    GetLanguagesAndProvidersRequest,
    GetLanguagesAndProvidersResponse,
    GetLanguagesResponse,
    GetProvidersForLanguageRequest,
    GetProvidersForLanguageResponse,
    GetSentencesRequest,
    GetSentencesResponse,
    GetSettingsResponse,
    GetSupportLinksResponse,
    GetTatoebaLanguagesResponse,
    Language,
    Provider,
    ProviderOptions,
    SearchShortcut,
    Sentence,
    TatoebaDownloadProgress,
)
from ..proto.generic_pb2 import Empty
from ..proto.services import BackendServiceBase
from ..providers import (
    get_languages as get_languages_base,
)
from ..providers import (
    get_provider,
    get_providers,
    get_sentences,
)
from ..providers import get_providers_for_language as get_providers_for_language_base
from ..providers.langs import get_all_languages
from ..providers.tatoeba import download_tatoeba_sentences


def fields_for_notes(mw: AnkiQt, nids: Iterable[NoteId]) -> list[str]:
    return mw.col.db.list(
        f"select distinct name from fields where ntid in (select mid from notes where id in {ids2str(nids)})"
    )


def get_languages() -> list[Language]:
    return [Language(code=code, name=name) for code, name in get_languages_base()]


def get_providers_for_language(lang: str) -> list[Provider]:
    return [
        Provider(code=provider.name, name=provider.human_name, url=provider.url)
        for provider in get_providers_for_language_base(lang)
    ]


def get_provider_field() -> list[str]:
    provider_field = config["provider_field"]
    if not provider_field:
        providers = []
        config["provider_field"] = ""
    else:
        providers = provider_field if isinstance(provider_field, list) else [provider_field]
    return providers


class BackendService(BackendServiceBase):
    tatoeba_download_progress: TatoebaDownloadProgress | None = None

    @classmethod
    def get_support_links(cls, request: Empty) -> GetSupportLinksResponse:
        github_page = consts.homepage
        forums_page = consts.support_channels["forums"]
        docs_page = consts.docs_page
        return GetSupportLinksResponse(github_page=github_page, forums_page=forums_page, docs_page=docs_page)

    @classmethod
    def get_tatoeba_languages(cls, request: Empty) -> GetTatoebaLanguagesResponse:
        return GetTatoebaLanguagesResponse(
            languages=[Language(code=code, name=name) for code, name in get_all_languages()]
        )

    @classmethod
    def download_tatoeba_sentences(cls, request: DownloadTatoebaSentencesRequest) -> Empty:
        def on_progress(progress: float, message: str, finished: bool) -> None:
            cls.tatoeba_download_progress = TatoebaDownloadProgress(
                progress=progress, message=message, is_error=False, finished=finished
            )

        def op(col: Collection) -> None:
            download_tatoeba_sentences(request.language, on_progress)

        def on_failure(exc: Exception) -> None:
            cls.tatoeba_download_progress = TatoebaDownloadProgress(progress=0.0, message=str(exc), is_error=True)
            logger.exception("Error downloading Tatoeba sentences", exc_info=exc)

        query_op = AddonQueryOp(parent=mw, op=op, success=lambda _: None).failure(on_failure).without_collection()
        mw.taskman.run_on_main(query_op.run_in_background)
        return Empty()

    @classmethod
    def get_tatoeba_download_progress(cls, request: Empty) -> TatoebaDownloadProgress:
        return cls.tatoeba_download_progress or TatoebaDownloadProgress(progress=0.0, message="", is_error=False)

    @classmethod
    def get_default_fill_fields(cls, request: GetDefaultFillFieldsRequest) -> GetDefaultFillFieldsResponse:
        providers = get_provider_field()
        return GetDefaultFillFieldsResponse(
            language=config["lang_field"],
            providers=providers,
            word_field=config["word_field"],
            sentences_field=config["sentences_field"],
            number_of_sentences=20,
            languages=get_languages(),
            language_providers=get_providers_for_language(config["lang_field"]),
            fields=fields_for_notes(mw, [NoteId(nid) for nid in request.nids]),
        )

    @classmethod
    def get_providers_for_language(cls, request: GetProvidersForLanguageRequest) -> GetProvidersForLanguageResponse:
        return GetProvidersForLanguageResponse(providers=get_providers_for_language(request.language))

    @classmethod
    def get_languages_and_providers(cls, request: GetLanguagesAndProvidersRequest) -> GetLanguagesAndProvidersResponse:
        language = request.default_language if request.HasField("default_language") else config["lang_field"]
        providers = get_provider_field()
        return GetLanguagesAndProvidersResponse(
            default_language=language,
            languages=get_languages(),
            providers=get_providers_for_language(language),
            default_providers=providers,
        )

    @classmethod
    def get_languages(cls, request: Empty) -> GetLanguagesResponse:
        return GetLanguagesResponse(languages=get_languages())

    @classmethod
    def get_sentences(cls, request: GetSentencesRequest) -> GetSentencesResponse:
        sentences: list[Sentence] = []
        for sentence in get_sentences(
            word=request.word,
            language=request.language,
            providers=list(request.providers),
        ):
            provider = get_provider(sentence.provider)
            sentences.append(
                Sentence(
                    text=sentence.text,
                    provider=provider.human_name,
                    source=sentence.source or provider.get_source(sentence.word, sentence.language),
                )
            )

        return GetSentencesResponse(sentences=sentences)

    @classmethod
    def get_settings(cls, request: Empty) -> GetSettingsResponse:
        search_shortcuts = []
        providers = get_provider_field()
        for shortcut in config["search_shortcuts"]:
            search_shortcuts.append(
                SearchShortcut(
                    keys=qt_key_to_js(shortcut["shortcut"]),
                    language=shortcut["language"],
                    selected_providers=shortcut["providers"],
                    providers=get_providers_for_language(shortcut["language"]),
                )
            )
        provider_options = [
            ProviderOptions(
                provider=Provider(code=provider.name, name=provider.human_name),
                options=json.dumps(config["provider_options"].get(provider.name, {})),
            )
            for provider in get_providers()
        ]
        return GetSettingsResponse(
            search_shortcuts=search_shortcuts,
            languages=get_languages(),
            default_language=config["lang_field"],
            default_providers=providers,
            language_providers=get_providers_for_language(config["lang_field"]),
            provider_options=provider_options,
        )
