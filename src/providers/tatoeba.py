from __future__ import annotations

import csv
import os
import re

from ..consts import consts
from ..db import Sentence
from ..vendor import pycountry
from .provider import SentenceProvider


class TatoebaProvider(SentenceProvider):
    name = "tatoeba"
    human_name = "Tatoeba"
    # TODO: add a way to indicate support for "all" or unspecified list of languages
    supported_languages = ["en", "tr", "ja", "ko", "zh"]

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        word = word.lower()
        # TODO: use a proper tokenizer/morphemizer for CJK languages
        # See MorphMan add-on
        pattern_str = (
            re.escape(word)
            if language in ("ja", "ko", "zh")
            else f"\\b{re.escape(word)}\\b"
        )
        pattern = re.compile(pattern_str)
        try:
            # Tatoeba uses ISO 639-3 codes
            alpha_3 = pycountry.languages.get(alpha_2=language).alpha_3.lower()
            with open(
                os.path.join(
                    consts.dir / "user_files", "tatoeba", f"{alpha_3}_sentences.tsv"
                ),
                encoding="utf-8",
                newline="",
            ) as f:
                reader = csv.reader(f, delimiter="\t")
                # TODO: maybe we can do better than reading the file each time
                # and iterating over all rows
                for row in reader:
                    sentence = row[2]
                    if pattern.search(sentence):
                        sentences.append(Sentence(sentence, word, language, self.name))
        except FileNotFoundError:
            pass
        return sentences

    def get_source(self, word: str, language: str) -> str:
        alpha_3 = pycountry.languages.get(alpha_2=language).alpha_3.lower()
        return (
            f"https://tatoeba.org/en/sentences/search?from={alpha_3}&query={word}&to="
        )
