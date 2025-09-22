import functools
import time
from typing import Any

from anki.collection import Collection, OpChangesWithCount
from anki.notes import NoteId
from aqt import mw
from aqt.operations import CollectionOp
from aqt.qt import QWidget
from aqt.utils import tooltip

from ..backend.server import get_server
from ..config import config
from ..consts import consts
from ..db import SentenceDB
from ..proto.backend_pb2 import FillInSentencesRequest
from ..providers import get_sentences
from .sveltekit_web import SveltekitWebDialog


class FillDialog(SveltekitWebDialog):
    key = "fill"

    def __init__(self, parent: QWidget, sentences_db: SentenceDB, nids: list[NoteId]):
        self.sentences_db = sentences_db
        self.nids = nids
        super().__init__(path="fill", parent=parent, subtitle="Fill in sentences")
        get_server().add_proto_handler_for_dialog(
            self,
            "ankiaddon.backend.BackendService",
            "FillInSentences",
            self._fill_in_sentences_request,
        )

    def get_query_params(self) -> dict[str, Any]:
        return {
            **super().get_query_params(),
            "nids": ",".join(str(nid) for nid in self.nids),
        }

    def _fill_in_sentences_request(self, data: bytes) -> bytes:
        request = FillInSentencesRequest.FromString(data)
        language = request.language
        providers = list(request.providers)
        word_field = request.word_field
        sentences_field = request.sentences_field
        number_of_sentences = request.number_of_sentences
        nids = request.nids

        def update_progress(i: int) -> None:
            mw.progress.update(
                f"Processed note {i + 1} of {len(nids)}...",
                value=i,
                max=len(nids),
            )

        def op(col: Collection) -> OpChangesWithCount:
            mw.taskman.run_on_main(lambda: mw.progress.set_title(consts.name))

            updated_notes = []
            last_progress = 0.0
            for i, nid in enumerate(nids):
                note = col.get_note(NoteId(nid))
                if word_field in note and sentences_field in note:
                    word = note[word_field]
                    sentences = get_sentences(
                        word=word,
                        language=language,
                        providers=providers,
                        limit=number_of_sentences,
                    )
                    note[sentences_field] = "<br>".join(
                        sentence.text for sentence in sentences
                    )
                    updated_notes.append(note)
                if time.time() - last_progress >= 0.1:
                    last_progress = time.time()
                    mw.taskman.run_on_main(functools.partial(update_progress, i=i))

            return OpChangesWithCount(
                count=len(updated_notes), changes=col.update_notes(updated_notes)
            )

        def success(changes: OpChangesWithCount) -> None:
            config["lang_field"] = language
            config["provider_field"] = providers[0] if providers else ""
            config["word_field"] = word_field
            config["sentences_field"] = sentences_field
            tooltip(f"Updated {changes.count} notes", parent=self.parentWidget())
            self.accept()

        collection_op = CollectionOp(parent=self, op=op).success(success)
        mw.taskman.run_on_main(collection_op.run_in_background)
        return b""
