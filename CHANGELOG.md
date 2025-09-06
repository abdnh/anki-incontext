# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2023-09-23

### Fixed

- Fixed error when deleting the add-on.

## [0.4.0] - 2023-07-04

### Added

- Added an interface to paste sentences to a chosen field.
- Added support for [Jisho](https://jisho.org/).

### Fixed

- Improved interface responsiveness with a lot of sentences.
- Fixed error on first card when cache is used

### Changed

- Words and sentences in the GUI are now aligned to the left.
- Default to first supported language if no language is provided in the template filter.
- Words added from the interface are now synced immediately.
- The refresh button now spins when loading sentences.

## [0.3.1] - 2023-05-29

### Fixed

- Fixed the add-on not being updated when installing an update.

## [0.3.0] - 2023-05-20

### Added

- Added a button to refresh sentences

## [0.2.0] - 2023-03-14

### Fixed

- Fixed the add-on sometimes hanging if a network request takes a lot of time.
- Sync all chosen providers when the sync button is clicked, instead of syncing only a randomly chosen one.

### Changed

- Fetch sentences in the background to avoid blocking card display.

## [0.1.0] - 2022-10-19

Initial release to AnkiWeb

### Fixed

- Fixed error caused by imported words that don't have sentences

### Added

- Allow deleting sentences and copying multiple ones.
- Allow the "Import sentences" button to handle multiple words.
- Support Dictionary.com
- The add-on's dialog now can be maximized.
- Preserve last used GUI options.

### Changed

- Use an archived version of Lexico.com because the site was shut down recently.

## [0.0.1] - 2022-07-03

Initial release

[0.4.1]: https://github.com/abdnh/anki-incontext/compare/0.4.0...0.4.1
[0.4.0]: https://github.com/abdnh/anki-incontext/compare/0.3.1...0.4.0
[0.3.1]: https://github.com/abdnh/anki-incontext/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/abdnh/anki-incontext/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/abdnh/anki-incontext/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/abdnh/anki-incontext/compare/0.0.1...0.1.0
[0.0.1]: https://github.com/abdnh/anki-incontext/commits/0.0.1
