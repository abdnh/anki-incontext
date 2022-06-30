.PHONY: all clean zip tdk tatoeba forms fix mypy

all: zip

zip: tdk tatoeba skell
	python -m ankibuild --type package --qt all --noconsts

ankiweb:
	python -m ankibuild --type ankiweb --qt all --noconsts

run: zip
	python -m ankirun

fix:
	python -m black src --exclude="forms|vendor"
	python -m isort src

mypy:
	python -m mypy .

tdk: src/providers/vendor/tdk.py

src/providers/vendor/tdk.py:
	curl https://raw.githubusercontent.com/abdnh/tdk/master/tdk.py -o $@

tatoeba: src/providers/vendor/tur_sentences.tsv

src/providers/vendor/tur_sentences.tsv:
	curl https://downloads.tatoeba.org/exports/per_language/tur/tur_sentences.tsv.bz2 -o src/providers/vendor/tur_sentences.tsv.bz2
	bzip2 -df $^

skell: src/providers/vendor/skell_downloader.py

src/providers/vendor/skell_downloader.py:
	curl https://raw.githubusercontent.com/abdnh/skell-downloader/master/skell_downloader.py -o $@

clean:
	rm -rf build/
