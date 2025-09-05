from __future__ import annotations

import functools
import time

from anki.collection import Collection, OpChangesWithCount
from anki.notes import NoteId
from anki.utils import ids2str
from aqt.main import AnkiQt
from aqt.operations import CollectionOp
from aqt.qt import QDialog, Qt, QWidget, qconnect
from aqt.utils import tooltip

from ..db import SentenceDB
from ..forms.fill import Ui_Dialog
from ..providers import get_languages, get_providers_for_language, get_sentences


def fields_for_notes(mw: AnkiQt, nids: list[NoteId]) -> list[str]:
    return mw.col.db.list(
        "select distinct name from fields where ntid in"
        f" (select mid from notes where id in {ids2str(nids)})"
    )


class FillDialog(QDialog):
    def __init__(
        self, parent: QWidget, mw: AnkiQt, sentences_db: SentenceDB, nids: list[NoteId]
    ):
        self.mw = mw
        self.sentences_db = sentences_db
        self.nids = nids
        QDialog.__init__(self, parent)
        self.config = mw.addonManager.getConfig(__name__)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.setup_ui()

    def setup_ui(self) -> None:
        self.setWindowTitle("InContext - Fill in sentences")
        for lang_code, lang_name in get_languages():
            self.form.language.addItem(lang_name, lang_code)
        last_lang = self.config["lang_field"]
        for idx in range(self.form.language.count()):
            if (
                self.form.language.itemData(idx, Qt.ItemDataRole.DisplayRole)
                == last_lang
            ):
                self.form.language.setCurrentIndex(idx)
                break
        self.populate_providers()
        last_provider = self.config["provider_field"]
        for idx in range(self.form.provider.count()):
            if (
                self.form.provider.itemData(idx, Qt.ItemDataRole.UserRole)
                == last_provider
            ):
                self.form.provider.setCurrentIndex(idx)
                break

        fields = fields_for_notes(self.mw, self.nids)
        last_word_field = self.config["word_field"]
        last_sentences_field = self.config["sentences_field"]
        for i, field in enumerate(fields):
            self.form.wordField.addItem(field)
            self.form.sentencesField.addItem(field)
            if field == last_word_field:
                self.form.wordField.setCurrentIndex(i)
            if field == last_sentences_field:
                self.form.sentencesField.setCurrentIndex(i)

        qconnect(self.form.language.currentIndexChanged, self.on_lang_changed)
        qconnect(self.form.processButton.clicked, self.on_process)
        qconnect(self.finished, self.on_finished)

    def on_finished(self) -> None:
        self.config["lang_field"] = self.form.language.currentText()
        self.config["provider_field"] = self.form.provider.currentData(
            Qt.ItemDataRole.UserRole
        )
        self.config["word_field"] = self.form.wordField.currentText()
        self.config["sentences_field"] = self.form.sentencesField.currentText()
        self.mw.addonManager.writeConfig(__name__, self.config)

    def on_lang_changed(self, index: int) -> None:
        self.populate_providers()

    def populate_providers(self) -> None:
        self.form.provider.clear()
        self.form.provider.addItem("All")
        for provider in get_providers_for_language(self.form.language.currentData()):
            self.form.provider.addItem(provider.human_name, provider.name)

    def on_process(self) -> None:
        lang = self.form.language.currentData()
        provider = (
            self.form.provider.currentData(Qt.ItemDataRole.UserRole)
            if self.form.provider.currentIndex()
            else None
        )
        word_field = self.form.wordField.currentText()
        sentences_field = self.form.sentencesField.currentText()
        number_of_sentences = self.form.numberOfSentences.value()

        def update_progress(i: int) -> None:
            self.mw.progress.update(
                f"Processed note {i + 1} of {len(self.nids)}...",
                value=i,
                max=len(self.nids),
            )

        def op(col: Collection) -> OpChangesWithCount:
            self.mw.taskman.run_on_main(lambda: self.mw.progress.set_title("InContext"))

            updated_notes = []
            last_progress = 0.0
            for i, nid in enumerate(self.nids):
                note = col.get_note(nid)
                if word_field in note and sentences_field in note:
                    word = note[word_field]
                    sentences = get_sentences(
                        word, lang, provider, limit=number_of_sentences
                    )
                    note[sentences_field] = "<br>".join(
                        sentence.text for sentence in sentences
                    )
                    updated_notes.append(note)
                if time.time() - last_progress >= 0.1:
                    last_progress = time.time()
                    self.mw.taskman.run_on_main(functools.partial(update_progress, i=i))

            return OpChangesWithCount(
                count=len(updated_notes), changes=col.update_notes(updated_notes)
            )

        def success(changes: OpChangesWithCount) -> None:
            self.accept()
            tooltip(f"Updated {changes.count} notes", parent=self.parentWidget())

        CollectionOp(self, op).success(success).run_in_background()
