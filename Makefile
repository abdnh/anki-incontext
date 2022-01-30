.PHONY: all format clean zip typecheck

all: zip

format:
	python -m black src

typecheck:
	python -m mypy src

zip: incontext.ankiaddon

incontext.ankiaddon: $(shell find src/ -type f) tdk
	rm -f $@
	rm -f src/meta.json
	rm -rf src/__pycache__
	( cd src/; zip -r ../$@ * )

forms: src/dialog.py

src/dialog.py: designer/dialog.ui
	pyuic5 $^ > $@

tdk: src/providers/vendor/tdk.py

src/providers/vendor/tdk.py:
	curl https://raw.githubusercontent.com/abdnh/tdk/master/tdk.py -o $@

clean:
	rm -f *.pyc
	rm -f src/*.pyc
	rm -f src/__pycache__
	rm -f incontext.ankiaddon
