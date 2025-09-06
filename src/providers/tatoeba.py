from __future__ import annotations

import bz2
import csv
import sqlite3
import tempfile
from pathlib import Path
from types import TracebackType
from typing import Callable

import requests

from ..consts import consts
from ..db import Sentence
from ..vendor import pycountry
from .provider import SentenceProvider


def tatoeba_db_path(language: str) -> Path:
    return consts.dir / "user_files" / "tatoeba" / f"{language}_sentences.db"


class TatoebaDB:
    def __init__(self, language: str):
        self.language = language
        alpha_3 = pycountry.languages.get(alpha_2=language).alpha_3.lower()
        self.conn = sqlite3.connect(tatoeba_db_path(alpha_3), check_same_thread=False)
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sentences (text TEXT);
            """
        )

    def __enter__(self) -> TatoebaDB:
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_value: Exception | None,
        traceback: TracebackType | None,
    ) -> None:
        self.conn.close()

    def add_sentences(self, sentences: list[str]) -> None:
        self.conn.executemany(
            """
            INSERT INTO sentences (text) VALUES (?)
            """,
            [(sentence,) for sentence in sentences],
        )
        self.conn.commit()

    def get_sentences(self, word: str) -> list[str]:
        params: tuple[str, ...]
        if self.language in ("ja", "ko", "zh"):
            # TODO: use a proper tokenizer/morphemizer for CJK languages
            query = "SELECT text FROM sentences WHERE text LIKE ?"
            params = (f"%{word}%",)
        else:
            query = """
            SELECT text FROM sentences WHERE
            text LIKE ? OR text LIKE ? OR text LIKE ? OR text LIKE ?
            """
            params = (
                f"{word} %",
                f"% {word}",
                f"% {word} %",
                word,
            )

        return [row[0] for row in self.conn.execute(query, params)]


def download_tatoeba_sentences(
    language: str, on_progress: Callable[[float, str], None]
) -> None:
    chunk_size = 8192
    with tempfile.NamedTemporaryFile() as bz2_file:
        url = f"https://downloads.tatoeba.org/exports/per_language/{language}/{language}_sentences.tsv.bz2"
        response = requests.get(url, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=chunk_size):
            bz2_file.write(chunk)
            on_progress(
                bz2_file.tell() / int(response.headers["Content-Length"]),
                "Downloading Tatoeba sentences",
            )
        bz2_file.seek(0)
        decompressor = bz2.BZ2Decompressor()
        with tempfile.NamedTemporaryFile(delete_on_close=False) as tsv_file:
            while True:
                try:
                    chunk = decompressor.decompress(bz2_file.read(), chunk_size)
                    tsv_file.write(chunk)
                    on_progress(
                        tsv_file.tell() / bz2_file.tell(),
                        "Decompressing Tatoeba sentences",
                    )
                except EOFError:
                    break
            tsv_file.close()
            with open(tsv_file.name, encoding="utf-8", newline="") as tsv_file2:
                with TatoebaDB(language) as db:
                    db.add_sentences(
                        [row[2] for row in csv.reader(tsv_file2, delimiter="\t")],
                    )


class TatoebaProvider(SentenceProvider):
    name = "tatoeba"
    human_name = "Tatoeba"
    # TODO: add a way to indicate support for "all" or unspecified list of languages
    supported_languages = ["en", "tr", "ja", "ko", "zh"]

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        word = word.lower()
        try:
            # Tatoeba uses ISO 639-3 codes
            with TatoebaDB(language) as db:
                sentences.extend(
                    Sentence(sentence, word, language, self.name)
                    for sentence in db.get_sentences(word)
                )
        except FileNotFoundError:
            pass
        return sentences

    def get_source(self, word: str, language: str) -> str:
        alpha_3 = pycountry.languages.get(alpha_2=language).alpha_3.lower()
        return (
            f"https://tatoeba.org/en/sentences/search?from={alpha_3}&query={word}&to="
        )
