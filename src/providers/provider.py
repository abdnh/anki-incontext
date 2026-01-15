from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, cast

from ..db import Sentence, SentenceDB
from ..exceptions import InContextUnsupportedLanguageError


@dataclass
class ProviderConfig:
    pass


T = TypeVar("T", bound=ProviderConfig)


class SentenceProvider(Generic[T], ABC):
    # Name used for identifying the provider in template filters and other places
    name: str
    # Name shown to the user in the GUI
    human_name: str
    # Website URL
    url: str
    config_class: type[T] = cast(type[T], ProviderConfig)

    def __init__(self, db: SentenceDB, config: dict[str, Any]):
        self.db = db
        self.config = self.config_class(**config)

    @property
    def supported_languages(self) -> list[str]:
        return []

    def get_cached_sentences(self, word: str, language: str, limit: int | None = None) -> list[Sentence]:
        try:
            with self.db.lock:
                return self.db.get_random_sentences(word, language, self.name, limit)
        except Exception:
            return []

    @abstractmethod
    def fetch(self, word: str, language: str) -> list[Sentence]:
        if language not in self.supported_languages:
            raise InContextUnsupportedLanguageError(language, self.name)
        return []

    def get_sentences(
        self,
        word: str,
        language: str | None,
        limit: int | None = None,
    ) -> list[Sentence]:
        sentences = []
        if not language:
            # Default to first supported language
            language = self.supported_languages[0]
        sentences.extend(self.get_cached_sentences(word, language, limit))
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
            "You should implement this method to provide a link or source "
            "from which the sentences are fetched for a given word."
        )
