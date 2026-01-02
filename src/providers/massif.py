from __future__ import annotations

from ..db import Sentence
from ..request import get_soup
from .provider import SentenceProvider


class MassifProvider(SentenceProvider):
    name = "massif"
    human_name = "Massif"
    url = "https://massif.la/ja/search?q={word}"

    @property
    def supported_languages(self) -> list[str]:
        return ["jpn"]

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)

        soup = get_soup(self.url.format(word=word))
        for sentence_li in soup.select("li.text-japanese"):
            sentence_div = sentence_li.select_one("div")
            if not sentence_div:
                continue
            text = sentence_div.get_text()
            sentences.append(
                Sentence(text=text, word=word, language=language, provider=self.name)
            )
        return sentences

    def get_source(self, word: str, language: str) -> str:
        return self.url.format(word=word)
