import random

import requests
from bs4 import BeautifulSoup


def _from_oxford(word):
    try:
        res = requests.get(f"https://www.lexico.com/definition/{word}?locale=en")
    except:
        return []
    b = BeautifulSoup(res.content, "html.parser")
    nodes = b.select(".ex")
    sentences = []
    for n in nodes:
        sentences.append(n.get_text())
    return sentences


def get_sentence(word):
    sentences = _from_oxford(word)
    if len(sentences) > 0:
        return random.choice(sentences)
    else:
        return ""
