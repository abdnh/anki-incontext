.PHONY: all format clean zip

all: zip

format:
	python -m black src

zip: incontext.ankiaddon

incontext.ankiaddon: src/*
	rm -f $@
	rm -f src/meta.json
	rm -rf src/__pycache__
	( cd src/; zip -r ../$@ * )

clean:
	rm -f *.pyc
	rm -f src/*.pyc
	rm -f src/__pycache__
	rm -f incontext.ankiaddon
