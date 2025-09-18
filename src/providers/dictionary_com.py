from __future__ import annotations

from ..db import Sentence
from ..request import get_soup
from .provider import SentenceProvider

# TODO: Also pull sentences that appear in the "How to use WORD in a sentence" section


class DictionaryProvider(SentenceProvider):
    name = "dictionary.com"
    human_name = "Dictionary.com"
    url = "https://www.dictionary.com/browse/{word}"

    @property
    def supported_languages(self) -> list[str]:
        return ["eng"]

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        soup = get_soup(self.url.format(word=word))
        nodes = soup.select('[data-type="example-sentences-module"] div p')
        for n in nodes:
            sentences.append(Sentence(n.get_text(), word, language, self.name))
        return sentences

    def get_source(self, word: str, language: str) -> str:
        return self.url.format(word=word)
