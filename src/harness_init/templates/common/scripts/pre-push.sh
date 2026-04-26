#!/bin/sh
# Pre-push hook: runs verification before allowing push.
# Install: ln -s ../../scripts/pre-push.sh .git/hooks/pre-push

set -e

echo "Running pre-push verification..."

if command -v make >/dev/null 2>&1; then
    make verify
else
    echo "make not found; running fallback checks..."
    ruff check src/
    pytest tests/ -v --cov=src --cov-fail-under=85
fi

echo "Pre-push verification passed."
