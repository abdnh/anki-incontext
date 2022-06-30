from typing import List, Sequence

from aqt.main import AnkiQt
from aqt.qt import *
from aqt.qt import qtmajor
from aqt.utils import getFile, getOnlyText

if qtmajor > 5:
    from .forms.form_qt6 import Ui_Dialog
else:
    from .forms.form_qt5 import Ui_Dialog  # type: ignore

from .providers import languages
from .sentences import fetch_sentences, read_sentences_db, update_sentences_db


class InContextDialog(QDialog):
    def __init__(self, mw: AnkiQt):
        self.mw = mw
        QDialog.__init__(self)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.setup_ui()

    def setup_ui(self) -> None:
        qconnect(self.form.words_list.currentItemChanged, self.populate_word_sentences)
        qconnect(self.form.add_word_button.clicked, self.on_add_word)
        qconnect(self.form.import_words_button.clicked, self.on_import_words)
        qconnect(self.form.import_sentences_button.clicked, self.on_import_sentences)
        qconnect(self.form.import_text_button.clicked, self.on_import_text)
        qconnect(self.form.sync_sentences_button.clicked, self.on_sync_sentences)
        qconnect(self.form.open_files_button.clicked, self.on_open_files)
        for ident, lang in languages.items():
            self.form.langComboBox.addItem(lang.name, ident)
        self.populate_words()
        qconnect(self.form.langComboBox.currentIndexChanged, self.on_lang_changed)

    def on_lang_changed(self, index: int) -> None:
        self.populate_words()

    def selected_words(self) -> List[str]:
        items = self.form.words_list.selectedItems()
        words = []
        for item in items:
            words.append(item.text())
        return words

    def selected_word(self) -> str:
        item = self.form.words_list.currentItem()
        return item.text() if item else ""

    def select_word(self, word: str) -> None:
        item = self.form.words_list.findItems(word, Qt.MatchFlag.MatchFixedString)[0]  # type: ignore[arg-type]
        self.form.words_list.setCurrentItem(item)

    def populate_words(self) -> None:
        lang = self.form.langComboBox.currentData()
        self.sentences_db = read_sentences_db(lang)
        self.refresh_words_list()

    def refresh_words_list(self) -> None:
        self.form.words_list.clear()
        self.form.words_list.addItems(self.sentences_db.keys())

    def populate_word_sentences(
        self, current: QListWidgetItem, previous: QListWidgetItem = None
    ) -> None:
        self.form.sentences_list.clear()
        if current:
            self.form.sentences_list.addItems(self.sentences_db[current.text()])

    def add_words(self, words: List[str]) -> None:
        for word in words:
            self.sentences_db.setdefault(word, [])
        lang = self.form.langComboBox.currentData()
        update_sentences_db(lang, self.sentences_db)
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

    def add_sentences(self, word: str, sentences: List[str]) -> None:
        self.sentences_db[word].extend(sentences)
        lang = self.form.langComboBox.currentData()
        update_sentences_db(lang, self.sentences_db)

    def on_import_sentences(self) -> None:
        word = self.selected_word()
        if not word:
            return

        sentences = []
        for sentence in self.form.textBox.toPlainText().split("\n"):
            sentences.append(sentence)
        self.add_sentences(word, sentences)
        self.populate_word_sentences(self.form.words_list.currentItem())  # type: ignore[arg-type]

    def on_import_text(self) -> None:
        for sentence in self.form.textBox.toPlainText().split("\n"):
            for word in sentence.split():
                d = self.sentences_db.get(word, [])
                d.append(sentence)
                self.sentences_db[word] = d
        lang = self.form.langComboBox.currentData()
        update_sentences_db(lang, self.sentences_db)
        self.refresh_words_list()

    def on_sync_sentences(self) -> None:
        lang = self.form.langComboBox.currentData()
        words = self.selected_words()
        for word in words:
            sentences = fetch_sentences(word, lang)
            # FIXME: just remove duplicates instead of clearing all sentences
            self.sentences_db[word] = []
            self.add_sentences(word, sentences)

        self.populate_word_sentences(self.form.words_list.currentItem())  # type: ignore[arg-type]

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
