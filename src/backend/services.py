from anki.collection import Collection
from aqt import mw
from aqt.operations import QueryOp

from ..log import logger
from ..proto.backend_pb2 import (
    DownloadTatoebaSentencesRequest,
    GetTatoebaLanguagesResponse,
    Language,
    TatoebaDownloadProgress,
)
from ..proto.generic_pb2 import Empty
from ..proto.services import BackendServiceBase
from ..providers.tatoeba import download_tatoeba_sentences, get_languages


class BackendService(BackendServiceBase):
    tatoeba_download_progress: TatoebaDownloadProgress | None = None

    @classmethod
    def get_tatoeba_languages(cls, request: Empty) -> GetTatoebaLanguagesResponse:
        return GetTatoebaLanguagesResponse(
            languages=[Language(code=code, name=name) for code, name in get_languages()]
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
