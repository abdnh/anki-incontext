from ..db import Sentence
from .provider import SentenceProvider
from .vendor.tdk import TDK


class TDKProvider(SentenceProvider):
    name = "tdk"
    supported_languages = {"tr"}

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        sentences.extend(
            Sentence(text, word, language, self.name) for text in TDK(word).examples
        )
        return sentences
