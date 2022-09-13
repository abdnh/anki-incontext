from ..db import Sentence
from ..request import get_soup
from .provider import SentenceProvider

# TODO: Also pull sentences that appear in the "How to use WORD in a sentence" section


class DictionaryProvider(SentenceProvider):
    name = "dictionary.com"
    human_name = "Dictionary.com"
    supported_languages = {"en"}
    url = "https://www.dictionary.com/browse/{word}"

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        soup = get_soup(self.url.format(word=word))
        nodes = soup.select(".luna-example")
        for n in nodes:
            sentences.append(Sentence(n.get_text(), word, language, self.name))
        return sentences

    def get_source(self, word: str, language: str) -> str:
        return self.url.format(word=word)
