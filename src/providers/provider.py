from __future__ import annotations

import random
from abc import ABC, abstractmethod

from ..db import Sentence, SentenceDB
from ..errors import InContextError


class SentenceProvider(ABC):
    # Name used for identifying the provider in template filters and other places
    name: str
    # Name shown to the user in the GUI
    human_name: str
    supported_languages: set[str]

    def __init__(self, db: SentenceDB):
        self.db = db

    def get_cached_sentences(
        self, word: str, language: str, limit: int | None = None
    ) -> list[Sentence]:
        try:
            with self.db.lock:
                return self.db.get_random_sentences(word, language, self.name, limit)
        except:
            return []

    @abstractmethod
    def fetch(self, word: str, language: str) -> list[Sentence]:
        if language not in self.supported_languages:
            raise InContextError(
                f'Language "{language}" is not supported by provider "{self.name}"'
            )
        return []

    # TODO: maybe fetch from all languages if language is None
    def get_sentences(
        self, word: str, language: str, use_cache: bool = True, limit: int | None = None
    ) -> list[Sentence]:
        sentences = []
        # FIXME: if use_cache=True, use cached sentences and fill rest of limit using fetched ones if necessary
        if use_cache:
            sentences.extend(self.get_cached_sentences(word, language, limit))
            if not limit:
                return sentences
        if not limit or len(sentences) < limit:
            fetched = self.fetch(word, language)
            if fetched:
                with self.db.lock:
                    self.db.add_sentences(fetched)
                sentences.extend(fetched)
        if sentences and limit and len(sentences) > limit:
            sentences = random.sample(sentences, limit)
        return sentences

    @abstractmethod
    def get_source(self, word: str, language: str) -> str:
        raise NotImplementedError(
            "You should implement this method to provide a link or source from which the sentences are fetched for a given word."
        )
