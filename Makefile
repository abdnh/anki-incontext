.PHONY: all clean zip fix mypy pylint vendor

all: zip

zip:
	python -m ankiscripts.build --type package --qt all --exclude user_files/**.db --exclude user_files/**/*.tsv

ankiweb:
	python -m ankiscripts.build --type ankiweb --qt all --exclude user_files/**.db --exclude user_files/**/*.tsv

vendor:
	./vendor.sh

fix:
	python -m black src tests --exclude="forms|vendor"
	python -m isort src tests

mypy:
	python -m mypy src tests

pylint:
	python -m pylint src tests

clean:
	rm -rf build/
