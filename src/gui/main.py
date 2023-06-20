from __future__ import annotations

from typing import Any, List, Sequence, cast

from aqt.main import AnkiQt
from aqt.qt import *
from aqt.qt import qtmajor
from aqt.utils import getFile, getOnlyText

from ..db import Sentence, SentenceDB
from ..providers import get_languages, get_providers_for_language, sync_sentences

if qtmajor > 5:
    from ..forms.main_qt6 import Ui_Dialog
else:
    from ..forms.main_qt5 import Ui_Dialog  # type: ignore


class InContextListView(QListView):
    currentIndexChanged = pyqtSignal(QModelIndex, QModelIndex)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.matches(QKeySequence.StandardKey.Copy):
            selected_indices = self.selectedIndexes()
            selected_text = []
            for idx in selected_indices:
                selected_text.append(idx.data(Qt.ItemDataRole.DisplayRole))
            QApplication.clipboard().setText("\n".join(selected_text) + "\n")
            return None
        return super().keyPressEvent(event)

    def currentChanged(self, current: QModelIndex, previous: QModelIndex) -> None:
        self.currentIndexChanged.emit(current, previous)
        return super().currentChanged(current, previous)


class WordListModel(QAbstractListModel):
    def __init__(
        self,
        db: SentenceDB,
        language: str,
        provider: str,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self.db = db
        self.language = language
        self.provider = provider
        self.words = list(
            {
                sentence.word
                for sentence in self.db.get_sentences(
                    language=language, provider=provider
                )
            }
        )

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.words)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        row = index.row()
        if role == Qt.ItemDataRole.DisplayRole:
            if row < len(self.words):
                return self.words[row]
        return None

    def removeRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveRows(QModelIndex(), row, row)
        word = self.words.pop(row)
        self.db.delete_sentences(
            word=word, language=self.language, provider=self.provider
        )
        self.endRemoveRows()
        return True

    def removeMultipleRows(self, rows: list[int]) -> None:
        if not rows:
            return
        self.beginRemoveRows(QModelIndex(), min(rows), max(rows))
        removed_words = [self.words[row] for row in rows]
        # TODO: add db method to remove sentences belonging to a list of words in bulk
        for word in removed_words:
            self.db.delete_sentences(
                word=word, language=self.language, provider=self.provider
            )
        self.words = [t for t in self.words if t not in removed_words]
        self.endRemoveRows()


class WordListView(InContextListView):
    def refresh_model(self, db: SentenceDB, language: str, provider: str) -> None:
        model = WordListModel(db, language, provider)
        self.setModel(model)
        # self.sortByColumn(ColumnFields.WORDS_FOUND.value, Qt.SortOrder.DescendingOrder)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Delete:
            indices = self.selectedIndexes()
            rows = []
            for index in indices:
                if index.isValid():
                    rows.append(index.row())
            self.model().removeMultipleRows(rows)
        return super().keyPressEvent(event)

    def model(self) -> WordListModel:
        return cast(WordListModel, super().model())


class SentenceListModel(QAbstractListModel):
    def __init__(
        self,
        db: SentenceDB,
        language: str,
        provider: str,
        word: str,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self.db = db
        self.language = language
        self.provider = provider
        self.word = word
        self.sentences = list(
            {
                sentence.text
                for sentence in self.db.get_sentences(
                    word=word,
                    language=language,
                    provider=provider,
                )
            }
        )

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.sentences)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        row = index.row()
        if role == Qt.ItemDataRole.DisplayRole:
            if row < len(self.sentences):
                return self.sentences[row]
        return None

    def removeRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveRows(QModelIndex(), row, row)
        sentence = self.sentences.pop(row)
        self.db.delete_sentence(
            sentence=sentence,
            word=self.word,
            language=self.language,
            provider=self.provider,
        )
        self.endRemoveRows()
        return True

    def removeMultipleRows(self, rows: list[int]) -> None:
        if not rows:
            return
        self.beginRemoveRows(QModelIndex(), min(rows), max(rows))
        removed_sentences = [self.sentences[row] for row in rows]
        for sentence in removed_sentences:
            self.db.delete_sentence(
                sentence=sentence,
                word=self.word,
                language=self.language,
                provider=self.provider,
            )
        self.sentences = [t for t in self.sentences if t not in removed_sentences]
        self.endRemoveRows()


class SentenceListView(InContextListView):
    def refresh_model(
        self, db: SentenceDB, language: str, provider: str, word: str
    ) -> None:
        model = SentenceListModel(db, language, provider, word)
        self.setModel(model)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Delete:
            indices = self.selectedIndexes()
            rows = []
            for index in indices:
                if index.isValid():
                    rows.append(index.row())
            self.model().removeMultipleRows(rows)
        return super().keyPressEvent(event)

    def model(self) -> SentenceListModel:
        return cast(SentenceListModel, super().model())


class InContextDialog(QDialog):
    def __init__(self, mw: AnkiQt, sentences_db: SentenceDB):
        self.mw = mw
        self.sentences_db = sentences_db
        QDialog.__init__(self, None, Qt.WindowType.Window)
        self.config = mw.addonManager.getConfig(__name__)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.setup_ui()

    def setup_ui(self) -> None:
        self.wordlist_view = WordListView()
        self.form.gridLayout.addWidget(self.wordlist_view, 4, 0)  # type: ignore[call-overload]
        self.sentencelist_view = SentenceListView()
        self.form.gridLayout.addWidget(self.sentencelist_view, 4, 1)  # type: ignore[call-overload]
        qconnect(self.wordlist_view.currentIndexChanged, self.populate_word_sentences)  # type: ignore[arg-type]
        qconnect(self.form.add_word_button.clicked, self.on_add_word)
        qconnect(self.form.import_words_button.clicked, self.on_import_words)
        qconnect(self.form.import_sentences_button.clicked, self.on_import_sentences)
        qconnect(self.form.import_text_button.clicked, self.on_import_text)
        qconnect(self.form.sync_sentences_button.clicked, self.on_sync_sentences)
        qconnect(self.form.open_files_button.clicked, self.on_open_files)
        for lang_code, lang_name in get_languages():
            self.form.langComboBox.addItem(lang_name, lang_code)
        last_lang = self.config["lang_field"]
        for idx in range(self.form.langComboBox.count()):
            if (
                self.form.langComboBox.itemData(idx, Qt.ItemDataRole.DisplayRole)
                == last_lang
            ):
                self.form.langComboBox.setCurrentIndex(idx)
                break
        self.populate_providers()
        last_provider = self.config["provider_field"]
        for idx in range(self.form.providerComboBox.count()):
            if (
                self.form.providerComboBox.itemData(idx, Qt.ItemDataRole.UserRole)
                == last_provider
            ):
                self.form.providerComboBox.setCurrentIndex(idx)
                break
        self.populate_words()
        qconnect(self.form.langComboBox.currentIndexChanged, self.on_lang_changed)
        qconnect(
            self.form.providerComboBox.currentIndexChanged, self.on_provider_changed
        )
        qconnect(self.finished, self.on_finished)

    def on_finished(self) -> None:
        self.config["lang_field"] = self.form.langComboBox.currentText()
        self.config["provider_field"] = self.form.providerComboBox.currentData(
            Qt.ItemDataRole.UserRole
        )
        self.mw.addonManager.writeConfig(__name__, self.config)

    def on_lang_changed(self, index: int) -> None:
        self.populate_providers()
        self.populate_words()

    def on_provider_changed(self) -> None:
        self.populate_words()

    def selected_words(self) -> List[str]:
        indices = self.wordlist_view.selectedIndexes()
        words = []
        for idx in indices:
            words.append(idx.data(Qt.ItemDataRole.DisplayRole))
        return words

    def selected_word(self) -> str:
        idx = self.wordlist_view.currentIndex()
        return idx.data(Qt.ItemDataRole.DisplayRole) if idx else ""

    def select_word(self, word: str) -> None:
        try:
            model = self.wordlist_view.model()
            indices = model.match(
                model.index(0, 0),
                Qt.ItemDataRole.DisplayRole,
                word,
                1,
                Qt.MatchFlag.MatchFixedString,
            )
            if indices:
                self.wordlist_view.setCurrentIndex(indices[0])
        except IndexError:
            pass

    def populate_words(self) -> None:
        self.refresh_words_list()

    def populate_providers(self) -> None:
        self.form.providerComboBox.clear()
        self.form.providerComboBox.addItem("All")
        for provider in get_providers_for_language(
            self.form.langComboBox.currentData()
        ):
            self.form.providerComboBox.addItem(provider.human_name, provider.name)

    def refresh_words_list(self) -> None:
        language = self.form.langComboBox.currentData()
        provider = (
            self.form.providerComboBox.currentData(Qt.ItemDataRole.UserRole)
            if self.form.providerComboBox.currentIndex()
            else None
        )
        self.wordlist_view.refresh_model(self.sentences_db, language, provider)

    def populate_word_sentences(
        self, current: QModelIndex, previous: QModelIndex = None
    ) -> None:
        if current:
            language = self.form.langComboBox.currentData()
            provider = (
                self.form.providerComboBox.currentData(Qt.ItemDataRole.UserRole)
                if self.form.providerComboBox.currentIndex()
                else None
            )
            word = current.data(Qt.ItemDataRole.DisplayRole)
            self.sentencelist_view.refresh_model(
                self.sentences_db, language, provider, word
            )

    def add_words(self, words: List[str]) -> None:
        lang = self.form.langComboBox.currentData()
        provider = (
            self.form.providerComboBox.currentData(Qt.ItemDataRole.UserRole)
            if self.form.providerComboBox.currentIndex()
            else None
        )
        for word in words:
            sync_sentences(word, lang, provider)
        self.refresh_words_list()

    def on_add_word(self) -> None:
        word = getOnlyText(prompt="Type a word", parent=self, title="InContext").strip()
        if not word:
            return
        self.add_words([word])
        self.select_word(word)

    def on_import_words(self) -> None:
        def import_files(filenames: Sequence[str]) -> None:
            words = []
            for filename in filenames:
                with open(filename, "r", encoding="utf-8") as f:
                    words.extend(f.read().split())
            self.add_words(words)

        getFile(self, title="Files to import", cb=import_files, multi=True)

    def add_sentences(
        self, word: str, sentence_texts: List[str], provider: str
    ) -> None:
        lang = self.form.langComboBox.currentData()
        sentences = []
        for text in sentence_texts:
            sentences.append(Sentence(text, word, lang, provider))
        self.sentences_db.add_sentences(sentences)

    def on_import_sentences(self) -> None:
        words = self.selected_words()
        if not words:
            return

        sentences = []
        for sentence in self.form.textBox.toPlainText().split("\n"):
            sentences.append(sentence)
        for word in words:
            self.add_sentences(word, sentences, "file")
        self.populate_word_sentences(self.wordlist_view.currentIndex())

    def on_import_text(self) -> None:
        lang = self.form.langComboBox.currentData()
        sentences: list[Sentence] = []
        for sentence in self.form.textBox.toPlainText().split("\n"):
            for word in sentence.split():
                sentences.append(Sentence(sentence, word, lang, "file"))
        self.sentences_db.add_sentences(sentences)
        self.refresh_words_list()

    def on_sync_sentences(self) -> None:
        lang = self.form.langComboBox.currentData()
        provider = (
            self.form.providerComboBox.currentData(Qt.ItemDataRole.UserRole)
            if self.form.providerComboBox.currentIndex()
            else None
        )
        words = self.selected_words()
        for word in words:
            sync_sentences(word, lang, provider, use_cache=False)

        self.populate_word_sentences(self.wordlist_view.currentIndex())

    def on_open_files(self) -> None:
        def import_files(filenames: Sequence[str]) -> None:
            self.form.textBox.clear()
            sentences = []
            for filename in filenames:
                with open(filename, "r", encoding="utf-8") as f:
                    for line in f:
                        sentence = line.strip()
                        sentences.append(sentence)
            self.form.textBox.setPlainText("\n".join(sentences))

        getFile(self, title="Files to import", cb=import_files, multi=True)
