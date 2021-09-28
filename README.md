# InContext

An Anki add-on that works as a template filter to show a random example sentence for vocabulary each time a card is viewed.

You just have to put a filter like this in your [card template](https://docs.ankiweb.net/templates/intro.html):
```
{{incontext:Front}}
```
Here the add-on will show a random example sentence according to the content of the `Front` field.
