from typing import List

import requests
from bs4 import BeautifulSoup

from .. import consts
from .vendor import SkellDownloader

skell_downloader = SkellDownloader(lang="English")

headers = {"User-Agent": consts.USER_AGENT}

# FIXME: If we search for "numbered" for example, the Oxford dict site doesn't redirect us to the entry of "number" here,
# while it does in a normal web browser. Changing the user agent string doesn't seem to help.


def from_oxford(word: str) -> List[str]:
    try:
        res = requests.get(
            f"https://www.lexico.com/definition/{word}?locale=en", headers=headers
        )
    except:
        return []
    b = BeautifulSoup(res.content, "html.parser")
    nodes = b.select(".ex")
    sentences = []
    for n in nodes:
        sentences.append(n.get_text())
    return sentences


def from_oxford_learner(word: str) -> List[str]:
    try:
        res = requests.get(
            f"https://www.oxfordlearnersdictionaries.com/definition/english/{word}",
            headers=headers,
        )
    except:
        return []
    b = BeautifulSoup(res.content, "html.parser")
    nodes = b.select(".x")
    sentences = []
    for n in nodes:
        sentences.append(n.get_text())
    return sentences


def from_skell(word: str) -> List[str]:
    return [str(s) for s in skell_downloader.get_examples(word)]


NAME = "English"
PROVIDERS = [from_oxford, from_oxford_learner, from_skell]
