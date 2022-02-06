import importlib
import os
from typing import List
import csv
import re

PROVIDERS_DIR = os.path.dirname(__file__)
VENDOR_DIR = os.path.join(PROVIDERS_DIR, "vendor")
spec = importlib.util.spec_from_file_location("tdk", os.path.join(VENDOR_DIR, "tdk.py"))
tdk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tdk)


def from_tdk(word: str) -> List[str]:
    return tdk.TDK(word).examples


def from_tatoeba(word: str) -> List[str]:
    word = word.lower()
    pattern = re.compile(f"\\b{re.escape(word)}\\b")
    matches = []
    try:
        with open(
            os.path.join(VENDOR_DIR, "tur_sentences.tsv"), encoding="utf-8", newline=""
        ) as f:
            reader = csv.reader(f, delimiter="\t")
            # FIXME: maybe we can do better than reading the file each time and iterating over all rows
            for row in reader:
                sentence = row[2]
                if pattern.search(sentence):
                    matches.append(sentence)
    except FileNotFoundError:
        pass
    return matches


NAME = "Turkish"
PROVIDERS = [from_tdk, from_tatoeba]
