from __future__ import annotations

import dataclasses
import sqlite3
from pathlib import Path
from threading import Lock
from types import TracebackType

from .consts import consts


@dataclasses.dataclass
class Sentence:
    text: str
    word: str
    language: str
    provider: str


class SentenceDB:
    # Schema upgrade code is adapted from https://github.com/ankitects/anki/blob/af8ae69837c0712b2c8be6b46a27191873d539c3/rslib/src/storage/sqlite.rs
    SCHEMA_STARTING_VERSION = 1
    SCHEMA_MAX_VERSION = 1

    def __init__(self, path: Path | None = None):
        self.con = sqlite3.connect(
            path or consts.dir / "user_files" / "sentences.db", check_same_thread=False
        )
        self.lock = Lock()
        self._open_or_create_db()

    def close(self) -> None:
        self.con.close()

    def __enter__(self) -> SentenceDB:
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_value: Exception | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _schema_version(self) -> tuple[bool, int]:
        with self.con:
            row = self.con.execute(
                "select null from sqlite_master where type = 'table' and name = 'col'"
            ).fetchall()
            if not row:
                return (True, self.SCHEMA_STARTING_VERSION)
            return (False, self.con.execute("select ver from col").fetchone()[0])

    def _open_or_create_db(self) -> None:
        with self.con:
            create, _ = self._schema_version()
            # upgrade = ver != self.SCHEMA_MAX_VERSION

            if create:
                self.con.executescript(
                    f"""
                CREATE TABLE sentences (
                    text TEXT,
                    word TEXT,
                    language TEXT,
                    provider TEXT,
                    PRIMARY KEY(text, word, language, provider)
                );
                CREATE TABLE col (
                    id INT PRIMARY KEY,
                    ver INT
                );
                INSERT INTO col(id, ver) VALUES (1, {self.SCHEMA_STARTING_VERSION});
                """
                )
            # if create or upgrade:
            #     self._upgrade_to_latest_schema(ver)

    def get_random_sentences(
        self, word: str, language: str, provider: str, limit: int | None = None
    ) -> list[Sentence]:
        sentences = []
        with self.con:
            query = "SELECT * from sentences WHERE word = ? AND language = ?"
            " AND provider = ? order by RANDOM()"
            if limit is not None:
                query += f" limit {limit}"
            for row in self.con.execute(
                query,
                (word, language, provider),
            ):
                sentences.append(Sentence(*row))
        return sentences

    def add_sentences(self, sentences: list[Sentence]) -> None:
        with self.con:
            self.con.executemany(
                """ INSERT OR REPLACE INTO sentences (text, word, language, provider)
                VALUES (?, ?, ?, ?) """,
                [
                    (
                        sentence.text,
                        sentence.word,
                        sentence.language,
                        sentence.provider,
                    )
                    for sentence in sentences
                ],
            )

    def get_sentences(
        self,
        word: str | None = None,
        language: str | None = None,
        provider: str | None = None,
    ) -> list[Sentence]:
        query = "SELECT * from sentences"
        where_clauses = []
        params = []
        if word:
            where_clauses.append("word = ?")
            params.append(word)
        if language:
            where_clauses.append("language = ?")
            params.append(language)
        if provider:
            where_clauses.append("provider = ?")
            params.append(provider)
        query += " WHERE " + " AND ".join(where_clauses)
        with self.con:
            sentences: list[Sentence] = []
            for row in self.con.execute(query, params):
                sentences.append(Sentence(*row))
            return sentences
