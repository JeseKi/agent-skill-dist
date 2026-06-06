.PHONY: check lint typecheck test build

check: lint typecheck test build

lint:
	uv run ruff check .

typecheck:
	uv run mypy

test:
	uv run pytest

build:
	uv build
