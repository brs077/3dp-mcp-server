.PHONY: install test test-integration lint format verify run clean list

install:
	uv sync

test:
	uv run pytest -m "not integration" -v

test-integration:
	uv run pytest -v

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

verify: lint test

run:
	uv run threedp-mcp

clean:
	rm -rf .venv outputs/ dist/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

list:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sed 's/:.*//' | sort
