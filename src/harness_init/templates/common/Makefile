.PHONY: verify test lint install

verify: lint test
	@echo "[OK] verified"

test:
	pytest tests/ -v --cov=src --cov-fail-under=85

lint:
	ruff check src/ tests/

install:
	pip install -e ".[dev]"
