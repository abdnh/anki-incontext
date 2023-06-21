from __future__ import annotations

from ..db import Sentence
from ..request import get_soup
from .provider import SentenceProvider


class GlosbeProvider(SentenceProvider):
    name = "glosbe"
    human_name = "Glosbe"
    # TODO: add a way to indicate support for "all" or unspecified list of languages
    supported_languages = ["en", "tr"]
    url = "https://glosbe.com/{language}/{language}/{word}"

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        soup = get_soup(self.url.format(language=language, word=word))
        for e in soup.select("#tmem_first_examples .tmem__item span"):
            sentences.append(Sentence(e.get_text().strip(), word, language, self.name))
        return sentences

    def get_source(self, word: str, language: str) -> str:
        return self.url.format(language=language, word=word)
