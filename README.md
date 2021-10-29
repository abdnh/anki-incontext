# InContext

An [Anki](https://apps.ankiweb.net/) add-on that works as a template filter to show random example sentences for vocabulary each time a card is viewed.

You just have to put a filter like this in your [card template](https://docs.ankiweb.net/templates/intro.html):
```
{{incontext:Front}}
```
Here the add-on will show a random example sentence containing the word in the `Front` field.

Currently, example sentences are fetched from the [Oxford English Dictionaries](https://www.lexico.com/) and the [Oxford Learner's Dictionaries](https://www.oxfordlearnersdictionaries.com/).
More sites and languages may be supported in the future.

Fetched sentences are saved locally in the `sentences.json` file and used in subsequent reviews of the same card.

Download this deck for a demo of the add-on: https://drive.google.com/file/d/1Era5ksSa59xjB3ZbVQsdoTbQEigzh6Bi/view?usp=sharing
