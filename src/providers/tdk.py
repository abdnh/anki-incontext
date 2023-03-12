from __future__ import annotations

from ..db import Sentence
from ..errors import InContextError
from .provider import SentenceProvider
from .vendor.tdk import TDK, TDKError


class TDKProvider(SentenceProvider):
    name = "tdk"
    human_name = "Türk Dil Kurumu Sözlükleri"
    supported_languages = {"tr"}

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        try:
            sentences.extend(
                Sentence(text, word, language, self.name) for text in TDK(word).examples
            )
        except TDKError as exc:
            raise InContextError(str(exc)) from exc
        return sentences

    def get_source(self, word: str, language: str) -> str:
        return "https://sozluk.gov.tr/"
