# InContext

An [Anki](https://apps.ankiweb.net/) add-on that fetches and displays example sentences in different languages from various sources.

## Fill-in option

You can add sentences to a chosen field in multiple notes using the browser's _Notes > InContext: Add sentences_ menu item.

![Fill-in dialog](images/fill.png)

## Template filter

The add-on also supports displaying random example sentences for vocabulary each time a card is viewed.

You just have to put a filter like this in your [card template](https://docs.ankiweb.net/templates/intro.html):

```
{{incontext:Front}}
```

Here, the add-on will show a random English example sentence containing the word in the `Front` field.

You can specify the language using the `lang` option:

```
{{incontext lang=en:Front}}
```

All [language codes](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes) supported by [Tatoeba](https://tatoeba.org/en/downloads) should work.

Sentences are fetched from multiple sources such as [Dictionary.com](https://www.dictionary.com/) (for English) and [sozluk.gov.tr](https://sozluk.gov.tr) (for Turkish).
You can show sentences from only a certain source by using the `provider` option, like this:

```
{{incontext lang=en provider=dictionary.com:Front}}
```

For a list of supported sources, see the [providers](./src/providers/) folder.
The identifier of each provider is defined by a `name` variable inside each provider class.
A list of available providers is also shown in the [interface](#interface).

If a provider is given but no language, the first supported language of the provider will be assumed.
If both language and provider are not given, the default is English with all providers.

More sites and languages will be added in the future. Contributions are welcome!

## Importing Tatoeba databases

Use _Tools > InContext > Download Tatoeba sentences_ to download sentences for your target language from [Tatoeba](https://tatoeba.org/).

## Browsing sentences

You can search for sentences using the screen under _Tools > InContext > Browse sentences_.

## Demo

Download this deck for a demo of the add-on: https://drive.google.com/file/d/1Era5ksSa59xjB3ZbVQsdoTbQEigzh6Bi/view?usp=sharing

## Download

You can download the add-on from its page on AnkiWeb: https://ankiweb.net/shared/info/385420176

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

## Credit

Some icons are adapted from [Bootstrap Icons](https://icons.getbootstrap.com/); licensed under the MIT.

## Support & feature requests

Please post any questions, bug reports, or feature requests in the [support page](https://forums.ankiweb.net/t/incontext-learn-vocabulary-in-context-with-random-sentences/24017) or the [issue tracker](https://github.com/abdnh/anki-incontext/issues).

If you want priority support for your feature/help request, I'm available for hire.
Get in touch via [email](mailto:abdo@abdnh.net) or the UpWork link below.

## Support me

Consider supporting me if you like my work:

<a href="https://github.com/sponsors/abdnh"><img height='36' src="https://i.imgur.com/dAgtzcC.png"></a>
<a href="https://www.patreon.com/abdnh"><img height='36' src="https://i.imgur.com/mZBGpZ1.png"></a>
<a href="https://www.buymeacoffee.com/abdnh" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" height="36" ></a>

I'm also available for freelance add-on development:

<a href="https://www.upwork.com/freelancers/~01d764ac58a0eccc5c"><img height='36' src="https://i.imgur.com/z9lPvHb.png"></a>
