.PHONY: verify test lint install

verify: lint test
	@echo "✅ 验证通过"

test:
	pytest tests/ -v --cov=src --cov-fail-under=85

lint:
	ruff check src/ tests/

install:
	pip install -e ".[dev]"