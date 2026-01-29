from __future__ import annotations

from ..db import Sentence
from ..vendor.skell_downloader import SkellDownloader
from .langs import langcode_to_name, search_language
from .provider import SentenceProvider


class SkellProvider(SentenceProvider):
    name = "skell"
    human_name = "SkELL"
    url = "https://skell.sketchengine.eu"

    @property
    def supported_languages(self) -> list[str]:
        langs = []
        for lang in SkellDownloader.langs:
            obj = search_language(lang)
            if obj:
                langs.append(obj.alpha_3)

        return langs

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        downloader = SkellDownloader(lang=langcode_to_name(language))
        for example in downloader.get_examples(word):
            sentences.append(Sentence(str(example), word, language, self.name))
        return sentences

    def get_source(self, word: str, language: str) -> str:
        return f"{self.url}/#result?lang={language}&query={word}&f=concordance"
