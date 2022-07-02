from ..db import Sentence
from ..request import get_soup
from .provider import SentenceProvider


class SesliSozlukProvider(SentenceProvider):
    name = "sesli_sozluk"
    supported_languages = {"tr"}

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        soup = get_soup(f"https://www.seslisozluk.net/{word}-nedir-ne-demek/")
        for e in soup.select('.ordered-list q[lang="tr"]'):
            sentences.append(Sentence(e.get_text(), word, language, self.name))
        return sentences
