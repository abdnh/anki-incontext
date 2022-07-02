from ..db import Sentence
from ..request import get_soup
from .provider import SentenceProvider


class SesliSozlukProvider(SentenceProvider):
    name = "sesli_sozluk"
    supported_languages = {"tr"}
    url = "https://www.seslisozluk.net/{word}-nedir-ne-demek/"

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        soup = get_soup(self.url.format(word=word))
        for e in soup.select('.ordered-list q[lang="tr"]'):
            sentences.append(Sentence(e.get_text(), word, language, self.name))
        return sentences

    def get_source(self, word: str, language: str) -> str:
        return self.url.format(word=word)
