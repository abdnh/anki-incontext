from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..db import Sentence, SentenceDB
from ..exceptions import InContextError
from ..vendor.nadeshiko_api_client.client import Client
from ..vendor.nadeshiko_api_client.models import SentenceSearchRequest
from .provider import ProviderConfig, SentenceProvider


class NadeshikoApiKeyError(InContextError):
    def __init__(self) -> None:
        super().__init__("Nadeshiko requires an API key. Configure it from Tools > InContext > Settings")


@dataclass
class NadeshikoConfig(ProviderConfig):
    api_key: str = ""


class NadeshikoProvider(SentenceProvider[NadeshikoConfig]):
    name = "nadeshiko"
    human_name = "Nadeshiko"
    url = "https://nadeshiko.co"
    config_class = NadeshikoConfig

    def __init__(self, db: SentenceDB, config: dict[str, Any]):
        super().__init__(db, config)
        self.client = Client(self.config.api_key)

    @property
    def supported_languages(self) -> list[str]:
        return ["jpn"]

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        if not self.config.api_key:
            raise NadeshikoApiKeyError()
        try:
            response = self.client.search_sentence(SentenceSearchRequest(query=word, limit=999))
            if response.sentences:
                for sentence in response.sentences:
                    source = (
                        f"https://nadeshiko.co/search/sentence?uuid={sentence.segment_info.uuid}"
                        if sentence.segment_info.uuid
                        else ""
                    )
                    if sentence.segment_info:
                        sentences.append(
                            Sentence(
                                text=sentence.segment_info.content_jp,
                                word=word,
                                language=language,
                                provider=self.name,
                                source=source,
                            )
                        )
        except Exception as exc:
            raise InContextError(str(exc)) from exc

        return sentences

    def get_source(self, word: str, language: str) -> str:
        return f"https://nadeshiko.co/search/sentence?query={word}"
