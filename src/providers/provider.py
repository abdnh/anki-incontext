from __future__ import annotations

import random
from abc import ABC, abstractmethod

from ..db import Sentence, SentenceDB
from ..errors import InContextError


class SentenceProvider(ABC):

    name: str
    supported_languages: set[str]

    def __init__(self, db: SentenceDB):
        self.db = db

    def get_cached_sentence(self, word: str, language: str) -> Sentence | None:
        try:
            return self.db.get_random_sentence(word, language, self.name)
        except:
            return None

    @abstractmethod
    def fetch(self, word: str, language: str) -> list[Sentence]:
        if language not in self.supported_languages:
            raise InContextError(
                f'Language "{language}" is not supported by provider "{self.name}"'
            )
        return []

    # TODO: maybe fetch from all languages if language is None
    def get_sentence(
        self, word: str, language: str, use_cache: bool = True
    ) -> Sentence | None:
        print(f"get_sentence: {word=} {language=} {use_cache=}")
        if use_cache:
            cached = self.get_cached_sentence(word, language)
            if cached:
                return cached
        fetched = self.fetch(word, language)
        if fetched:
            self.db.add_sentences(fetched)
            return random.choice(fetched)
        return None
