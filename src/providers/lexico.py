from __future__ import annotations

from ..db import Sentence
from ..request import get_soup
from .provider import SentenceProvider

# FIXME: If we search for "numbered" for example,
# the Oxford dict site doesn't redirect us to the entry of "number" here,
# while it does in a normal web browser.
# Changing the user agent string doesn't seem to help.


class LexicoProvider(SentenceProvider):
    name = "lexico"
    human_name = "Lexico"
    supported_languages = ["en"]
    url = (
        "https://web.archive.org/web/https://www.lexico.com/definition/{word}?locale=en"
    )

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        soup = get_soup(self.url.format(word=word))
        nodes = soup.select(".ex")
        for n in nodes:
            sentences.append(Sentence(n.get_text(), word, language, self.name))
        return sentences

    def get_source(self, word: str, language: str) -> str:
        return self.url.format(word=word)
