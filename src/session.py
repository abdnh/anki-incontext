from __future__ import annotations

from .db import SentenceDB
from .providers import init_providers

sentences_db: SentenceDB | None = None


def init_db() -> None:
    global sentences_db
    sentences_db = SentenceDB()
    init_providers(sentences_db)


def get_db() -> SentenceDB:
    assert sentences_db is not None, "DB not initialized"
    return sentences_db
