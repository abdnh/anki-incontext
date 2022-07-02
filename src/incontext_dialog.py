from typing import List, Sequence

from aqt.main import AnkiQt
from aqt.qt import *
from aqt.qt import qtmajor
from aqt.utils import getFile, getOnlyText

from .db import Sentence, SentenceDB
from .providers import get_languages, get_providers_for_language, get_sentence

if qtmajor > 5:
    from .forms.form_qt6 import Ui_Dialog
else:
    from .forms.form_qt5 import Ui_Dialog  # type: ignore


class InContextDialog(QDialog):
    def __init__(self, mw: AnkiQt, sentences_db: SentenceDB):
        self.mw = mw
        self.sentences_db = sentences_db
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
        for (lang_code, lang_name) in get_languages():
            self.form.langComboBox.addItem(lang_name, lang_code)
        self.populate_providers()
        self.populate_words()
        qconnect(self.form.langComboBox.currentIndexChanged, self.on_lang_changed)
        qconnect(
            self.form.providerComboBox.currentIndexChanged, self.on_provider_changed
        )

    def on_lang_changed(self, index: int) -> None:
        self.populate_providers()
        self.populate_words()

    def on_provider_changed(self) -> None:
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
        # pylint: disable=no-member
        try:
            item = self.form.words_list.findItems(word, Qt.MatchFlag.MatchFixedString)[0]  # type: ignore[arg-type]
            self.form.words_list.setCurrentItem(item)
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
            self.form.providerComboBox.addItem(provider)

    def refresh_words_list(self) -> None:
        lang = self.form.langComboBox.currentData()
        provider = (
            self.form.providerComboBox.currentText()
            if self.form.providerComboBox.currentIndex()
            else None
        )
        self.form.words_list.clear()
        self.form.words_list.addItems(
            {
                sentence.word
                for sentence in self.sentences_db.get_sentences(
                    language=lang, provider=provider
                )
            }
        )

    def populate_word_sentences(
        self, current: QListWidgetItem, previous: QListWidgetItem = None
    ) -> None:
        self.form.sentences_list.clear()
        if current:
            lang = self.form.langComboBox.currentData()
            provider = (
                self.form.providerComboBox.currentText()
                if self.form.providerComboBox.currentIndex()
                else None
            )
            word = current.text()
            self.form.sentences_list.addItems(
                {
                    sentence.text
                    for sentence in self.sentences_db.get_sentences(
                        word=word,
                        language=lang,
                        provider=provider,
                    )
                }
            )

    def add_words(self, words: List[str]) -> None:
        lang = self.form.langComboBox.currentData()
        provider = (
            self.form.providerComboBox.currentText()
            if self.form.providerComboBox.currentIndex()
            else None
        )
        for word in words:
            get_sentence(word, lang, provider)
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
        word = self.selected_word()
        if not word:
            return

        sentences = []
        for sentence in self.form.textBox.toPlainText().split("\n"):
            sentences.append(sentence)
        self.add_sentences(word, sentences, "file")
        self.populate_word_sentences(self.form.words_list.currentItem())  # type: ignore[arg-type]

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
            self.form.providerComboBox.currentText()
            if self.form.providerComboBox.currentIndex()
            else None
        )
        words = self.selected_words()
        for word in words:
            get_sentence(word, lang, provider, use_cache=False)

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
