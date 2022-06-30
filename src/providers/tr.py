import csv
import os
import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .. import consts
from .vendor import TDK


def from_tdk(word: str) -> List[str]:
    return TDK(word).examples


def from_tatoeba(word: str) -> List[str]:
    word = word.lower()
    pattern = re.compile(f"\\b{re.escape(word)}\\b")
    matches = []
    try:
        with open(
            os.path.join(consts.VENDOR_DIR, "tur_sentences.tsv"),
            encoding="utf-8",
            newline="",
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


def from_seslisozluk(word: str) -> List[str]:
    try:
        req = requests.get(
            f"https://www.seslisozluk.net/{word}-nedir-ne-demek/",
            headers={"User-Agent": consts.USER_AGENT},
        )
    except:
        return []
    soup = BeautifulSoup(req.text, "html.parser")
    sentences = []
    for e in soup.select('.ordered-list q[lang="tr"]'):
        sentences.append(e.get_text())
    # for e in soup.select('.similar.ordered-list + dd q[lang=en]'):
    #     sentences.append(e.get_text())
    return sentences


# TODO: generalize to all supported languages
def from_glosbe(word: str) -> List[str]:
    try:
        req = requests.get(
            f"https://glosbe.com/tr/en/{word}",
            headers={"User-Agent": consts.USER_AGENT},
        )
    except:
        return []
    soup = BeautifulSoup(req.text, "html.parser")
    sentences = []
    for e in soup.select("#tmem_first_examples .tmem__item [lang=tr]"):
        sentences.append(e.get_text().strip())
    return sentences


NAME = "Turkish"
PROVIDERS = [from_tdk, from_tatoeba, from_seslisozluk, from_glosbe]
