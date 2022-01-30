import os
import random
import json
from typing import Dict, List

from .providers import languages


def sentences_file_for_lang(lang: str) -> str:
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), f"user_files/{lang}_sentences.json"
    )


langs = ["en", "tr"]


def ensure_sentence_files_exist():
    for lang in langs:
        sentences_file = sentences_file_for_lang(lang)
        if not os.path.exists(sentences_file):
            with open(sentences_file, "w", encoding="utf-8") as f:
                f.write("{}\n")


ensure_sentence_files_exist()


def read_sentences_db(lang: str) -> Dict[str, List[str]]:
    with open(sentences_file_for_lang(lang), "r", encoding="utf-8") as f:
        return json.load(f)


def update_sentences_db(lang: str, db: Dict[str, List[str]]):
    with open(sentences_file_for_lang(lang), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)


def fetch_sentences(word: str, lang: str) -> List[str]:
    sentences = []
    for provider in languages[lang]["providers"]:
        sentences.extend(provider(word))
    return sentences


def get_sentence(word: str, lang: str) -> str:
    word = word.strip()
    local_db = read_sentences_db(lang)
    if not word:
        # choose a sentence from all sentences in the DB if an empty word is given
        sentences = [s for l in local_db.values() for s in l]
    else:
        sentences = local_db.get(word, [])
        if len(sentences) <= 0:
            sentences = fetch_sentences(word, lang)
            local_db[word] = sentences
            update_sentences_db(lang, local_db)
    if len(sentences) > 0:
        sentence = random.choice(sentences)
        return sentence
    else:
        return ""
