default: zip

UV_RUN := "uv run --"

BUILD_ARGS := "--qt all --exclude user_files/**/*"

# Package add-on for AnkiWeb
ankiweb:
	{{UV_RUN}} python -m ankiscripts.build --type ankiweb {{BUILD_ARGS}}

# Package add-on for distribution outside of AnkiWeb
zip:
	{{UV_RUN}} python -m ankiscripts.build --type package --qt all {{BUILD_ARGS}}

# Install dependencies to src/vendor
vendor:
	{{UV_RUN}} python -m ankiscripts.vendor --exclude pycountry/locales

# Format using Ruff
ruff:
	{{UV_RUN}} pre-commit run -a ruff-format

# Check formatting using Ruff
ruff-check:
	{{UV_RUN}} ruff check

# Format using dprint
dprint:
	{{UV_RUN}} pre-commit run -a dprint

# Check type hints using mypy
mypy:
	-{{UV_RUN}} pre-commit run -a mypy

# Run ts+svelte checks
ts-check:
  cd ts && npm run check && npm run lint

# Fix formatting issues
fix: ruff dprint

# Run mypy+formatting+ts checks
lint: mypy ruff-check ts-check

# Run pytest
pytest:
  {{UV_RUN}} python -m  pytest

# Run ts tests
ts-test:
  cd ts && npm run test

# Run pytest+ts tests
test: pytest ts-test

# Package source distribution
sourcedist:
	{{UV_RUN}} python -m ankiscripts.sourcedist

# Clean up build files
clean:
	rm -rf build/
