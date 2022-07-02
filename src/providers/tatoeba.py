import csv
import os
import re

import pycountry

from .. import consts
from ..db import Sentence
from .provider import SentenceProvider


class TatoebaProvider(SentenceProvider):
    name = "tatoeba"
    # TODO: add a way to indicate support for "all" or unspecified list of languages
    supported_languages = {"en", "tr"}

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        word = word.lower()
        pattern = re.compile(f"\\b{re.escape(word)}\\b")
        try:
            # Tatoeba uses ISO 639-3 codes
            alpha_3 = pycountry.languages.get(alpha_2=language).alpha_3.lower()
            with open(
                os.path.join(
                    consts.USERFILES_DIR, "tatoeba", f"{alpha_3}_sentences.tsv"
                ),
                encoding="utf-8",
                newline="",
            ) as f:
                reader = csv.reader(f, delimiter="\t")
                # TODO: maybe we can do better than reading the file each time and iterating over all rows
                for row in reader:
                    sentence = row[2]
                    if pattern.search(sentence):
                        sentences.append(Sentence(sentence, word, language, self.name))
        except FileNotFoundError:
            pass
        return sentences
