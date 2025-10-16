from __future__ import annotations

from collections.abc import Iterable

from anki.collection import Collection
from anki.notes import NoteId
from anki.utils import ids2str
from aqt import mw
from aqt.main import AnkiQt
from aqt.operations import QueryOp

from ..config import config
from ..log import logger
from ..proto.backend_pb2 import (
    DownloadTatoebaSentencesRequest,
    GetDefaultFillFieldsRequest,
    GetDefaultFillFieldsResponse,
    GetLanguagesResponse,
    GetProvidersForLanguageRequest,
    GetProvidersForLanguageResponse,
    GetSentencesRequest,
    GetSentencesResponse,
    GetTatoebaLanguagesResponse,
    Language,
    Provider,
    Sentence,
    TatoebaDownloadProgress,
)
from ..proto.generic_pb2 import Empty
from ..proto.services import BackendServiceBase
from ..providers import (
    get_languages,
    get_provider,
    get_providers_for_language,
    get_sentence_source,
    get_sentences,
)
from ..providers.langs import get_all_languages
from ..providers.tatoeba import download_tatoeba_sentences


def fields_for_notes(mw: AnkiQt, nids: Iterable[NoteId]) -> list[str]:
    return mw.col.db.list(
        "select distinct name from fields where ntid in"
        f" (select mid from notes where id in {ids2str(nids)})"
    )


class BackendService(BackendServiceBase):
    tatoeba_download_progress: TatoebaDownloadProgress | None = None

    @classmethod
    def get_tatoeba_languages(cls, request: Empty) -> GetTatoebaLanguagesResponse:
        return GetTatoebaLanguagesResponse(
            languages=[
                Language(code=code, name=name) for code, name in get_all_languages()
            ]
        )

    @classmethod
    def download_tatoeba_sentences(
        cls, request: DownloadTatoebaSentencesRequest
    ) -> Empty:
        def on_progress(progress: float, message: str, finished: bool) -> None:
            cls.tatoeba_download_progress = TatoebaDownloadProgress(
                progress=progress, message=message, is_error=False, finished=finished
            )

        def op(col: Collection) -> None:
            download_tatoeba_sentences(request.language, on_progress)

        def on_failure(exc: Exception) -> None:
            cls.tatoeba_download_progress = TatoebaDownloadProgress(
                progress=0.0, message=str(exc), is_error=True
            )
            logger.exception("Error downloading Tatoeba sentences", exc_info=exc)

        query_op = QueryOp(parent=mw, op=op, success=lambda _: None).failure(on_failure)
        mw.taskman.run_on_main(query_op.run_in_background)
        return Empty()

    @classmethod
    def get_tatoeba_download_progress(cls, request: Empty) -> TatoebaDownloadProgress:
        return cls.tatoeba_download_progress or TatoebaDownloadProgress(
            progress=0.0, message="", is_error=False
        )

    @classmethod
    def get_default_fill_fields(
        cls, request: GetDefaultFillFieldsRequest
    ) -> GetDefaultFillFieldsResponse:
        provider_field = config["provider_field"]
        providers = (
            provider_field if isinstance(provider_field, list) else [provider_field]
        )
        return GetDefaultFillFieldsResponse(
            language=config["lang_field"],
            providers=providers,
            word_field=config["word_field"],
            sentences_field=config["sentences_field"],
            number_of_sentences=20,
            languages=[
                Language(code=code, name=name) for code, name in get_languages()
            ],
            language_providers=[
                Provider(code=provider.name, name=provider.human_name)
                for provider in get_providers_for_language(config["lang_field"])
            ],
            fields=fields_for_notes(mw, [NoteId(nid) for nid in request.nids]),
        )

    @classmethod
    def get_providers_for_language(
        cls, request: GetProvidersForLanguageRequest
    ) -> GetProvidersForLanguageResponse:
        return GetProvidersForLanguageResponse(
            providers=[
                Provider(code=provider.name, name=provider.human_name)
                for provider in get_providers_for_language(request.language)
            ]
        )

    @classmethod
    def get_languages(cls, request: Empty) -> GetLanguagesResponse:
        return GetLanguagesResponse(
            languages=[Language(code=code, name=name) for code, name in get_languages()]
        )

    @classmethod
    def get_sentences(cls, request: GetSentencesRequest) -> GetSentencesResponse:
        return GetSentencesResponse(
            sentences=[
                Sentence(
                    text=sentence.text,
                    provider=get_provider(sentence.provider).human_name,
                    url=get_sentence_source(sentence),
                )
                for sentence in get_sentences(
                    word=request.word,
                    language=request.language,
                    providers=list(request.providers),
                )
            ]
        )
