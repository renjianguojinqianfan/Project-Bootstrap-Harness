.PHONY: verify test lint format-check format install

verify: lint format-check test
	@echo "[OK] verified"

test:
	pytest tests/ -v --cov=src --cov-fail-under=85

lint:
	ruff check src/ tests/

format-check:
	ruff format --check src/ tests/

format:
	ruff format src/ tests/

install:
	pip install -e ".[dev]"
