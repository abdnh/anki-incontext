from __future__ import annotations

from ..db import Sentence
from ..request import get_soup
from .provider import SentenceProvider


class OxfordLearnerProvider(SentenceProvider):
    name = "oxford_learner"
    human_name = "Oxford Learner's Dictionaries"
    url = "https://www.oxfordlearnersdictionaries.com"
    search_url = "{url}/definition/english/{word}"

    @property
    def supported_languages(self) -> list[str]:
        return ["eng"]

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        soup = get_soup(self.search_url.format(url=self.url, word=word))
        # FIXME: report errors
        nodes = soup.select(".x")
        for n in nodes:
            sentences.append(Sentence(n.get_text(), word, language, self.name))
        return sentences

    def get_source(self, word: str, language: str) -> str:
        return self.search_url.format(url=self.url, word=word)
