from __future__ import annotations

from ..db import Sentence
from ..request import get_soup
from .langs import get_all_languages
from .provider import SentenceProvider


class GlosbeProvider(SentenceProvider):
    name = "glosbe"
    human_name = "Glosbe"
    url = "https://glosbe.com"
    search_url = "{url}/{language}/{language}/{word}"

    @property
    def supported_languages(self) -> list[str]:
        return [code for code, _ in get_all_languages()]

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        soup = get_soup(self.search_url.format(url=self.url, language=language, word=word))
        for e in soup.select("#tmem_first_examples .tmem__item span"):
            sentences.append(Sentence(e.get_text().strip(), word, language, self.name))
        return sentences

    def get_source(self, word: str, language: str) -> str:
        return self.search_url.format(url=self.url, language=language, word=word)
