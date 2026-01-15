from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..db import Sentence, SentenceDB
from ..exceptions import InContextError
from ..vendor.nadeshiko_api_client import ApiClient, ApiException, Configuration, SearchApi, SentenceSearchRequest
from .provider import ProviderConfig, SentenceProvider


@dataclass
class NadeshikoConfig(ProviderConfig):
    api_key: str


class NadeshikoProvider(SentenceProvider[NadeshikoConfig]):
    name = "nadeshiko"
    human_name = "Nadeshiko"
    url = "https://nadeshiko.co"
    config_class = NadeshikoConfig

    def __init__(self, db: SentenceDB, config: dict[str, Any]):
        super().__init__(db, config)
        configuration = Configuration()
        configuration.api_key["apiKeyHeader"] = self.config.api_key
        self.client = ApiClient(configuration)

    @property
    def supported_languages(self) -> list[str]:
        return ["jpn"]

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        api_instance = SearchApi(self.client)
        context_request = SentenceSearchRequest(query=word)
        try:
            api_response = api_instance.search_sentence(context_request)
            for sentence in api_response.sentences:
                # TODO: the `uuid` field can be used to construct a sentence-specific source (https://github.com/abdnh/anki-incontext/issues/32)
                sentences.append(
                    Sentence(text=sentence.segment_info.content_jp, word=word, language=language, provider=self.name)
                )
        except ApiException as exc:
            raise InContextError(str(exc)) from exc

        return sentences

    def get_source(self, word: str, language: str) -> str:
        return f"https://nadeshiko.co/search/sentence?query={word}"
