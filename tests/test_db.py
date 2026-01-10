from pathlib import Path

from src.db import Sentence, SentenceDB


def test_add(tmpdir: Path) -> None:
    with SentenceDB(tmpdir / "sentences.db") as db:
        db.add_sentences([Sentence(text="Hello, world!", word="world", language="en", provider="test")])
        sentences = db.get_sentences(word="world", language="en", provider="test")
        assert len(sentences) == 1
        assert sentences[0].text == "Hello, world!"
        assert sentences[0].word == "world"
        assert sentences[0].language == "en"
        assert sentences[0].provider == "test"
