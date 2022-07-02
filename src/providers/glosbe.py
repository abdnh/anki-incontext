from ..db import Sentence
from ..request import get_soup
from .provider import SentenceProvider


class GlosbeProvider(SentenceProvider):
    name = "glosbe"
    # TODO: add a way to indicate support for "all" or unspecified list of languages
    supported_languages = {"en", "tr"}

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        soup = get_soup(f"https://glosbe.com/{language}/{language}/{word}")
        for e in soup.select("#tmem_first_examples .tmem__item span"):
            sentences.append(Sentence(e.get_text().strip(), word, language, self.name))
        return sentences
