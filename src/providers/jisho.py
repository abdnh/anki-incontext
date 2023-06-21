from __future__ import annotations

from ..db import Sentence
from ..request import get_soup
from .provider import SentenceProvider


class JishoProvider(SentenceProvider):
    name = "jisho"
    human_name = "Jisho"
    supported_languages = ["ja"]
    url = "https://jisho.org/search/{word} %23sentences"

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        page = 1
        while True:
            soup = get_soup(f"{self.url}?page={page}".format(word=word, page=page))
            sentence_elements = soup.select(".japanese_sentence ")
            if not sentence_elements:
                break
            for sentence_element in sentence_elements:
                for el in sentence_element.select(".furigana"):
                    el.decompose()
                sentences.append(
                    Sentence(sentence_element.get_text(), word, language, self.name)
                )
            page += 1
        return sentences

    def get_source(self, word: str, language: str) -> str:
        return self.url.format(word=word)
