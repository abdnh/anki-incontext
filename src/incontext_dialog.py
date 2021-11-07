from typing import List

from PyQt5 import QtCore
from aqt.qt import *
from aqt.utils import getOnlyText, getFile

from .dialog import Ui_Dialog
from .sentences import read_sentences_db, update_sentences_db, fetch_sentences


class InContextDialog(QDialog):
    def __init__(self, mw):
        self.mw = mw
        QDialog.__init__(self)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.form.words_list.currentItemChanged.connect(self.populate_word_sentences)
        self.form.add_word_button.clicked.connect(self.on_add_word)
        self.form.import_words_button.clicked.connect(self.on_import_words)
        self.form.add_sentence_button.clicked.connect(self.on_add_sentence)
        self.form.import_sentences_button.clicked.connect(self.on_import_sentences)
        self.form.sync_sentences_button.clicked.connect(self.on_sync_sentences)
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

    def select_word(self, word: str):
        item = self.form.words_list.findItems(
            word, QtCore.Qt.MatchFlag.MatchFixedString
        )[0]
        self.form.words_list.setCurrentItem(item)

    def populate_words(self):
        self.sentences_db = read_sentences_db()
        self.refresh_words_list()

    def refresh_words_list(self):
        self.form.words_list.clear()
        self.form.words_list.addItems(self.sentences_db.keys())

    def populate_word_sentences(
        self, current: QListWidgetItem, previous: QListWidgetItem = None
    ):
        self.form.sentences_list.clear()
        if current:
            self.form.sentences_list.addItems(self.sentences_db[current.text()])

    def add_words(self, words):
        for word in words:
            self.sentences_db.setdefault(word, [])
        update_sentences_db(self.sentences_db)
        self.refresh_words_list()

    def on_add_word(self):
        word = getOnlyText(prompt="Type a word", parent=self, title="InContext").strip()
        if not word:
            return
        self.add_words([word])
        self.select_word(word)

    def on_import_words(self):
        def import_files(filenames):
            words = []
            for filename in filenames:
                with open(filename, "r", encoding="utf-8") as f:
                    words.extend(f.read().split())
            self.add_words(words)

        getFile(self, title="Files to import", cb=import_files, multi=True)

    def add_sentences(self, word: str, sentences: List[str]):
        self.sentences_db[word].extend(sentences)
        update_sentences_db(self.sentences_db)

    def on_add_sentence(self):
        word = self.selected_word()
        if not word:
            return
        sentence = getOnlyText(
            prompt="Type a sentence", parent=self, title="InContext"
        ).strip()
        if not sentence:
            return
        self.add_sentences(word, [sentence])
        self.populate_word_sentences(self.form.words_list.currentItem())

    def on_import_sentences(self):
        word = self.selected_word()
        if not word:
            return

        def import_files(filenames):
            sentences = []
            for filename in filenames:
                with open(filename, "r", encoding="utf-8") as f:
                    sentences.extend(map(lambda l: l.strip(), f.readlines()))
            self.add_sentences(word, sentences)
            self.populate_word_sentences(self.form.words_list.currentItem())

        getFile(self, title="Files to import", cb=import_files, multi=True)

    def on_sync_sentences(self):
        words = self.selected_words()
        for word in words:
            sentences = fetch_sentences(word)
            # FIXME: just remove duplicates instead of clearing all sentences
            self.sentences_db[word] = []
            self.add_sentences(word, sentences)

        self.populate_word_sentences(self.form.words_list.currentItem())
