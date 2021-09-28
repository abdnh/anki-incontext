import os
import random
import json

import requests
from bs4 import BeautifulSoup

sentences_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "sentences.json"
)


def _from_oxford(word: str):
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


def get_sentence(word: str):
    if not word.strip():
        return ""
    if not os.path.exists(sentences_file):
        with open(sentences_file, "w", encoding="utf-8") as f:
            f.write("{}\n")
    with open(sentences_file, "r", encoding="utf-8") as f:
        local_db = json.load(f)
    sentences = local_db.get(word, [])
    if len(sentences) <= 0:
        sentences = _from_oxford(word)
        local_db[word] = sentences
        with open(sentences_file, "w", encoding="utf-8") as f:
            json.dump(local_db, f, ensure_ascii=False, indent=4)
    if len(sentences) > 0:
        sentence = random.choice(sentences)
        return sentence
    else:
        return ""
