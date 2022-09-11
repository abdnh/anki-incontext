from ..db import Sentence
from .provider import SentenceProvider
from .vendor.skell_downloader import SkellDownloader


class SkellProvider(SentenceProvider):
    name = "skell"
    human_name = "SkELL"
    # TODO: add all languages supported by Skell
    supported_languages = {"en"}

    def fetch(self, word: str, language: str) -> list[Sentence]:
        sentences = super().fetch(word, language)
        # FIXME: convert language codes to names before passing them to downloader
        downloader = SkellDownloader(lang="English")
        for example in downloader.get_examples(word):
            sentences.append(Sentence(str(example), word, language, self.name))
        return sentences

    def get_source(self, word: str, language: str) -> str:
        return f"https://skell.sketchengine.eu/#result?lang={language}&query={word}&f=concordance"
