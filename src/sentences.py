import os
import random
import json

import requests
from bs4 import BeautifulSoup

sentences_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "sentences.json"
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0"
}

# FIXME: If we search for "numbered" for example, the Oxford dict site doesn't redirect us to the entry of "number" here,
# while it does in a normal web browser. Changing the user agent string doesn't seem to help.


def _from_oxford(word: str):
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


def _from_oxford_learner(word: str):
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


def fetch_sentences(word: str):
    providers = [_from_oxford, _from_oxford_learner]
    sentences = []
    for provider in providers:
        sentences.extend(provider(word))
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
        sentences = fetch_sentences(word)
        local_db[word] = sentences
        with open(sentences_file, "w", encoding="utf-8") as f:
            json.dump(local_db, f, ensure_ascii=False, indent=4)
    if len(sentences) > 0:
        sentence = random.choice(sentences)
        return sentence
    else:
        return ""
