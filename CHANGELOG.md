# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.6] = 2026-02-14

### Fixed

- Fix error when updating the add-on on Windows. You might need to download the add-on package from here on GitHub and run it with Anki closed to apply the update correctly. If you don't need to preserve your settings, you can just delete the add-on completely and reinstall it.

## [1.4.5] = 2026-02-14

### Fixed

- Fixed an error when a lookup in the SKELL website returns no results.

## [1.4.4] = 2026-01-30

### Fixed

- Fixed error when opening add-on screens such Browse multiple times.

## [1.4.3] - 2026-01-29

### Fixed

- Fixed SKELL provider no longer working.

### Changed

- The page listing languages/providers was moved from _Tools > InContext > Help_ to _Tools > InContext > Languages_. The Help page now lists support links.

## [1.4.2] - 2026-01-24

### Added

- Added a basic usage [manual](https://www.abdnh.net/anki-incontext/).

### Fixed

- Fixed crammed provider names in Browse screen.

### Changed

- Some sentence source links (e.g. Jisho) now take you to the sentence-specific URL in the provider's website instead of the general search page.

## [1.4.1] - 2026-01-16

### Fixed

- Fix startup error if Nadeshiko API key is not set.

## [1.4.0] - 2026-01-15

### Added

- Add a help page under _Tools > InContext > Languages_ listing all supported languages and providers.
- Add support for [Nadeshiko](https://nadeshiko.co/). API key can be configured in the Settings page.

## [1.3.0] - 2026-01-11

### Changed

- Redesign UI for more consistent colors and dark mode support.
- Search shortcuts now do not open a new Browse window if there's already one open.

### Added

- Add options to set default language and providers for Browse and Fill-in windows.

## [1.2.3] - 2026-01-06

### Added

- Support specifying multiple comma-separated providers in the template filter.
- Add a shortcut (Ctrl+F) to focus search field in the Browse page.
- Align sentence source to the right in the Browse page.

## [1.2.2] - 2026-01-03

### Fixed

- Do not react to text copied form the Browse page (when the clipboard monitor is enabled).

## [1.2.1] - 2026-01-02

### Fixed

- Fixed clipboard monitor in the Browse page crashing Anki after a few lookups.

## [1.2.0] - 2026-01-02

### Added

- Add a provider for [Massif](https://massif.la/ja).
- Add a button to the Browse page to trigger search on clipboard changes.

## [1.1.2] - 2025-12-23

### Fixed

- Fixed template filters blocking card rendering with a progress dialog.
- Fixed sentences from previous cards appearing on the current card for a few seconds.

## [1.1.1] - 2025-10-30

### Fixed

- Fixed search shortcut's providers not working.

## [1.1.0] - 2025-10-30

### Added

- Allow searching for sentences in the Browse screen using shortcuts (Set in Tools > InContext > Settings).

## [1.0.2] - 2025-10-16

### Fixed

- Fixed error if no provider is set.
- Fixed filter errors not being properly reported to user.

## [1.0.1] - 2025-10-16

### Fixed

- Report errors during initial load of browse/fill screens.

## [1.0.0] - 2025-10-16

### Changed

- The Fill screen has been redesigned.

### Removed

- Removed Lexico provider.
- Removed Manage screen.

### Fixed

- Fixed Dictionary.com provider

### Added

- Added an option to import Tatoeba databases(see [README.md](./README.md)).
- Added a new screen to search for sentences (_Tools > InContext > Browse sentences_).

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

[1.4.6]: https://github.com/abdnh/anki-incontext/compare/1.4.5...1.4.6
[1.4.5]: https://github.com/abdnh/anki-incontext/compare/1.4.4...1.4.5
[1.4.4]: https://github.com/abdnh/anki-incontext/compare/1.4.3...1.4.4
[1.4.3]: https://github.com/abdnh/anki-incontext/compare/1.4.2...1.4.3
[1.4.2]: https://github.com/abdnh/anki-incontext/compare/1.4.1...1.4.2
[1.4.1]: https://github.com/abdnh/anki-incontext/compare/1.4.0...1.4.1
[1.4.0]: https://github.com/abdnh/anki-incontext/compare/1.3.0...1.4.0
[1.3.0]: https://github.com/abdnh/anki-incontext/compare/1.2.3...1.3.0
[1.2.3]: https://github.com/abdnh/anki-incontext/compare/1.2.2...1.2.3
[1.2.2]: https://github.com/abdnh/anki-incontext/compare/1.2.1...1.2.2
[1.2.1]: https://github.com/abdnh/anki-incontext/compare/1.2.0...1.2.1
[1.2.0]: https://github.com/abdnh/anki-incontext/compare/1.1.2...1.2.0
[1.1.2]: https://github.com/abdnh/anki-incontext/compare/1.1.1...1.1.2
[1.1.1]: https://github.com/abdnh/anki-incontext/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/abdnh/anki-incontext/compare/1.0.2...1.1.0
[1.0.2]: https://github.com/abdnh/anki-incontext/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/abdnh/anki-incontext/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/abdnh/anki-incontext/compare/0.4.1...1.0.0
[0.4.1]: https://github.com/abdnh/anki-incontext/compare/0.4.0...0.4.1
[0.4.0]: https://github.com/abdnh/anki-incontext/compare/0.3.1...0.4.0
[0.3.1]: https://github.com/abdnh/anki-incontext/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/abdnh/anki-incontext/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/abdnh/anki-incontext/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/abdnh/anki-incontext/compare/0.0.1...0.1.0
[0.0.1]: https://github.com/abdnh/anki-incontext/commits/0.0.1
