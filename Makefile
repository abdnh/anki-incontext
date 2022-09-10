.PHONY: all clean zip fix mypy pylint vendor

all: zip

zip:
	python -m ankibuild --type package --qt all --noconsts --exclude user_files/**.db --exclude user_files/**/*.tsv

ankiweb:
	python -m ankibuild --type ankiweb --qt all --noconsts --exclude user_files/**.db --exclude user_files/**/*.tsv

run:
	python -m ankirun

vendor:
	./vendor.sh

fix:
	python -m black src --exclude="forms|vendor"
	python -m isort src

mypy:
	python -m mypy .

pylint:
	python -m pylint src

clean:
	rm -rf build/
