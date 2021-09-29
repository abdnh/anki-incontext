.PHONY: all format clean zip

all: zip

format:
	python -m black src

zip: build.zip

build.zip: src/*
	rm -f $@
	rm -f src/meta.json
	rm -rf src/__pycache__
	( cd src/; zip -r ../$@ * )
	cp build.zip incontext.ankiaddon

clean:
	rm -f *.pyc
	rm -f src/*.pyc
	rm -f src/__pycache__
	rm -f build.zip
	rm -f incontext.ankiaddon
