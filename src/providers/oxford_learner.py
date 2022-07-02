from ..db import Sentence
from ..request import get_soup
from .provider import SentenceProvider


class OxfordLearnerProvider(SentenceProvider):
    name = "oxford_learner"
    supported_languages = {"en"}

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        soup = get_soup(
            f"https://www.oxfordlearnersdictionaries.com/definition/english/{word}"
        )
        # FIXME: report errors
        nodes = soup.select(".x")
        for n in nodes:
            sentences.append(Sentence(n.get_text(), word, language, self.name))
        return sentences
