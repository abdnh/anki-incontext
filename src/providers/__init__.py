from __future__ import annotations

import random

from ..db import Sentence, SentenceDB
from .dictionary_com import DictionaryProvider
from .glosbe import GlosbeProvider
from .jisho import JishoProvider
from .langs import get_language_info, langcode_to_name
from .oxford_learner import OxfordLearnerProvider
from .provider import SentenceProvider
from .seslisozluk import SesliSozlukProvider
from .skell import SkellProvider
from .tatoeba import TatoebaProvider
from .tdk import TDKProvider

PROVIDER_CLASSES: list[type[SentenceProvider]] = [
    TatoebaProvider,
    GlosbeProvider,
    OxfordLearnerProvider,
    SkellProvider,
    TDKProvider,
    SesliSozlukProvider,
    DictionaryProvider,
    JishoProvider,
]
PROVIDERS: list[SentenceProvider] = []


def init_providers(db: SentenceDB) -> None:
    PROVIDERS.clear()
    for cls in PROVIDER_CLASSES:
        PROVIDERS.append(cls(db))


def get_sentences(
    word: str,
    language: str | None = None,
    providers: list[str] | None = None,
    limit: int | None = None,
) -> list[Sentence]:
    # Default to English if no language and provider is given
    if not (language or providers):
        language = "eng"
    if len(providers) == 0:
        return []
    language = get_language_info(language).alpha_3.lower()
    matched_providers: list[SentenceProvider] = []
    for provider_obj in PROVIDERS:
        matched = True
        if language:
            matched &= (
                language in provider_obj.supported_languages
                or langcode_to_name(language) in provider_obj.supported_languages
            )
        if providers:
            matched &= provider_obj.name in providers
        if matched:
            matched_providers.append(provider_obj)
    random.shuffle(matched_providers)
    sentences: list[Sentence] = []
    while matched_providers and (not limit or len(sentences) < limit):
        chosen_provider = matched_providers.pop()
        sentences.extend(chosen_provider.get_sentences(word, language, limit))
    if sentences and limit and len(sentences) > limit:
        sentences = random.sample(sentences, limit)
    return sentences


def sync_sentences(
    word: str,
    language: str | None = None,
    provider: str | None = None,
) -> None:
    matched_providers: list[SentenceProvider] = []
    for provider_obj in PROVIDERS:
        matched = True
        if language:
            matched &= (
                language in provider_obj.supported_languages
                or langcode_to_name(language) in provider_obj.supported_languages
            )
        if provider:
            matched &= provider == provider_obj.name
        if matched:
            matched_providers.append(provider_obj)
    random.shuffle(matched_providers)
    while matched_providers:
        chosen_provider = matched_providers.pop()
        chosen_provider.get_sentences(word, language)


def get_languages() -> list[tuple[str, str]]:
    langs = set()
    for provider in PROVIDERS:
        langs.update(provider.supported_languages)
    return [(code, langcode_to_name(code)) for code in langs]


def get_providers_for_language(language: str) -> list[SentenceProvider]:
    providers = []
    for provider in PROVIDERS:
        if language in provider.supported_languages:
            providers.append(provider)
    return providers


def get_provider(name: str) -> SentenceProvider | None:
    for provider in PROVIDERS:
        if provider.name == name:
            return provider
    return None


def get_sentence_source(sentence: Sentence) -> str:
    provider = get_provider(sentence.provider)
    if provider:
        return provider.get_source(sentence.word, sentence.language)
    return ""
