.PHONY: all format clean zip typecheck tdk tatoeba forms

all: zip

format:
	python -m black src

typecheck:
	python -m mypy src

PACKAGE_NAME := incontext

zip: $(PACKAGE_NAME).ankiaddon

$(PACKAGE_NAME).ankiaddon: $(shell find src/ -type f) tdk tatoeba skell
	rm -f $@
	rm -f src/meta.json
	rm -rf src/__pycache__
	rm -rf src/providers/__pycache__
	rm -rf src/providers/vendor/__pycache__
	( cd src/; zip -r ../$@ * )

forms: src/form.py

src/form.py: designer/form.ui
	pyuic5 $^ > $@

# install in test profile
install: zip
	# rm -r ankiprofile/addons21/$(PACKAGE_NAME)
	cp -r src/. ankiprofile/addons21/$(PACKAGE_NAME)


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
	rm -f *.pyc
	rm -f src/*.pyc
	rm -f src/__pycache__
	rm -f $(PACKAGE_NAME).ankiaddon
