from concurrent.futures import Future
from typing import cast

import requests
from aqt.main import AnkiQt
from aqt.qt import QComboBox, QFormLayout, QPushButton, qconnect
from aqt.utils import tooltip
from bs4 import BeautifulSoup, Tag

from ..providers.tatoeba import download_tatoeba_sentences
from .dialog import Dialog


def get_languages() -> list[str]:
    response = requests.get("https://downloads.tatoeba.org/exports/per_language/")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    codes = [str(cast(Tag, lang)["href"]).split("/")[0] for lang in soup.find_all("a")]
    return [code for code in codes if code not in ("..", "unknown")]


class TatoebaDialog(Dialog):
    def __init__(self, mw: AnkiQt):
        self.mw = mw
        super().__init__(mw)

    def setup_ui(self) -> None:
        super().setup_ui()
        layout = QFormLayout(self)
        self.combobox = QComboBox(self)
        layout.addRow("Language", self.combobox)
        self.download_button = QPushButton("Download", self)
        layout.addRow(self.download_button)

        self.mw.taskman.with_progress(
            get_languages,
            on_done=lambda f: self._on_fetched_languages(f.result()),
            parent=self,
            label="Fetching languages...",
        )

    def _on_fetched_languages(self, languages: list[str]) -> None:
        for code in languages:
            self.combobox.addItem(code)

        qconnect(self.download_button.clicked, self._on_download)

    def _on_download(self) -> None:
        language = self.combobox.currentText()

        def on_progress(progress: float, message: str) -> None:
            self.mw.taskman.run_on_main(
                lambda: self.mw.progress.update(
                    label=message, value=int(progress * 100), max=100
                )
            )

        def task() -> None:
            download_tatoeba_sentences(language, on_progress)

        self.mw.taskman.with_progress(
            task,
            on_done=self._on_download_done,
            parent=self,
        )

    def _on_download_done(self, future: Future) -> None:
        self.mw.progress.finish()
        future.result()
        self.close()
        tooltip("Downloaded Tatoeba sentences", parent=self.mw)
