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
    GetProvidersForLanguageRequest,
    GetProvidersForLanguageResponse,
    GetTatoebaLanguagesResponse,
    Language,
    Provider,
    TatoebaDownloadProgress,
)
from ..proto.generic_pb2 import Empty
from ..proto.services import BackendServiceBase
from ..providers import get_languages, get_providers_for_language
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
        return GetDefaultFillFieldsResponse(
            language=config["lang_field"],
            provider=config["provider_field"],
            word_field=config["word_field"],
            sentences_field=config["sentences_field"],
            number_of_sentences=20,
            languages=[
                Language(code=code, name=name) for code, name in get_languages()
            ],
            providers=[
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
