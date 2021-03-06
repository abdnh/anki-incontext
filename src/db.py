from __future__ import annotations

import dataclasses
import sqlite3

from . import consts


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

    def __init__(self, path: str | None = None):
        self.con = sqlite3.connect(path or consts.DB_FILE)
        self._open_or_create_db()

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

    def get_random_sentence(self, word: str, language: str, provider: str) -> Sentence:
        with self.con:
            row = self.con.execute(
                "SELECT * from sentences WHERE word = ? AND language = ? AND provider = ? order by RANDOM() limit 1",
                (word, language, provider),
            ).fetchone()
            return Sentence(*row)

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

    # def remove_sentences(self, sentences: list[Sentence]) -> None:
    #     with self.con:
    #         self.con.executemany(
    #             """
    #         DELETE FROM sentences
    #         WHERE text = ? AND word = ? AND language = ? AND provider = ?""",
    #             [
    #                 (sentence.text, sentence.word, sentence.language, sentence.provider)
    #                 for sentence in sentences
    #             ],
    #         )

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
