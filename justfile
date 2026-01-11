default: zip

set windows-shell := ["pwsh", "-c"]

UV_RUN := "uv run --"

BUILD_ARGS := "--qt all --exclude user_files/*.db --exclude user_files/**/*"

# Package add-on for AnkiWeb
ankiweb:
	{{UV_RUN}} python -m ankiscripts.build --type ankiweb {{BUILD_ARGS}}

# Package add-on for distribution outside of AnkiWeb
zip:
	{{UV_RUN}} python -m ankiscripts.build --type package --qt all {{BUILD_ARGS}}

# Install dependencies to src/vendor
vendor:
	{{UV_RUN}} python -m ankiscripts.vendor

# Format using Ruff
ruff *files:
	{{UV_RUN}} ruff format --force-exclude {{files}}

# Check formatting and lints using Ruff
ruff-check *files:
	{{UV_RUN}} ruff check --force-exclude --fix {{files}}

# Format using dprint
dprint *files:
	dprint fmt --allow-no-files {{files}}

# Check type hints using mypy
mypy *files:
	{{UV_RUN}} mypy {{files}}

# Run ts+svelte checks
ts-check:
  {{ if path_exists("ts") == "true" { "cd ts && npm run check && npm run lint" } else { "" } }}

# Check proto files for formatting issues
proto-check *files:
  {{ if path_exists("ts") == "true" { "cd ts && npm run check_proto" } else { "" } }}

# Format proto files
proto:
  {{ if path_exists("ts") == "true" { "cd ts && npm run format_proto" } else { "" } }}

# Fix formatting issues
fix: ruff dprint proto

# Run mypy+formatting+ts+proto checks
lint: mypy ruff-check ts-check proto-check

# Run pytest
pytest:
  {{UV_RUN}} python -m  pytest

# Run ts tests
ts-test:
  {{ if path_exists("ts") == "true" { "cd ts && npm run test" } else { "" } }}


# Run pytest+ts tests
test: pytest ts-test

# Package source distribution
sourcedist:
	{{UV_RUN}} python -m ankiscripts.sourcedist

# Clean up build files
clean:
	rm -rf build/
