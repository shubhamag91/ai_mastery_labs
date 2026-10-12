# Shortcuts for the routines every lab uses. Run `make <target>` from the repo root.
.PHONY: test lint fmt data

test:  ## Run the test suite
	uv run pytest

lint:  ## Check code without changing it (what pre-commit and CI check)
	uv run ruff check .
	uv run ruff format --check .

fmt:  ## Fix what can be fixed automatically
	uv run ruff check --fix .
	uv run ruff format .

DATAGEN = uv run --group datagen python -m scripts.datagen

data:  ## Rebuild data/ from data/SPEC.md, replaying cached LLM text (no API calls once cached)
	$(DATAGEN).tables
	$(DATAGEN).reviews
	$(DATAGEN).docs
	$(DATAGEN).calls
	$(DATAGEN).images build
	$(DATAGEN).manifest
