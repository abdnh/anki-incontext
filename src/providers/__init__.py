from __future__ import annotations

import random
from typing import Type

import pycountry

from ..db import Sentence, SentenceDB
from .glosbe import GlosbeProvider
from .lexico import LexicoProvider
from .oxford_learner import OxfordLearnerProvider
from .provider import SentenceProvider
from .seslisozluk import SesliSozlukProvider
from .skell import SkellProvider
from .tatoeba import TatoebaProvider
from .tdk import TDKProvider

PROVIDER_CLASSES: list[Type[SentenceProvider]] = [
    TatoebaProvider,
    GlosbeProvider,
    LexicoProvider,
    OxfordLearnerProvider,
    SkellProvider,
    TDKProvider,
    SesliSozlukProvider,
]
PROVIDERS: list[SentenceProvider] = []


def init_providers(db: SentenceDB) -> None:
    for cls in PROVIDER_CLASSES:
        PROVIDERS.append(cls(db))


def get_sentence(
    word: str,
    language: str | None = None,
    provider: str | None = None,
    use_cache: bool = True,
) -> Sentence | None:
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
    sentence: Sentence | None = None
    random.shuffle(matched_providers)
    while matched_providers and not sentence:
        chosen_provider = matched_providers.pop()
        sentence = chosen_provider.get_sentence(word, language, use_cache)
    return sentence


def langcode_to_name(lang_code: str) -> str:
    try:
        return pycountry.languages.get(alpha_2=lang_code).name
    except AttributeError:
        return lang_code


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
