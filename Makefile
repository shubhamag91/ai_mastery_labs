# Shortcuts for the routines every lab uses. Run `make <target>` from the repo root.
.PHONY: test lint fmt

test:  ## Run the test suite
	uv run pytest

lint:  ## Check code without changing it (what pre-commit and CI check)
	uv run ruff check .
	uv run ruff format --check .

fmt:  ## Fix what can be fixed automatically
	uv run ruff check --fix .
	uv run ruff format .
