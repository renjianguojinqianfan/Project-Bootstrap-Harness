# Pre-push hook for Windows PowerShell.
# Runs verification before allowing git push.
#
# Install: Copy this file to .git/hooks/pre-push (remove .ps1 extension).
# Git for Windows executes hook files with no extension.
# Alternatively, set core.hooksPath to scripts/ (requires Git >= 2.36).
#
# For environments without `make` installed (common on Windows),
# this script falls back to running ruff and pytest directly.

$ErrorActionPreference = 'Stop'

Write-Host "Running pre-push verification..."

$make = Get-Command make -ErrorAction SilentlyContinue

if ($make) {
    Write-Host "Found make; running 'make verify'..."
    make verify
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Host "make not found; running fallback checks..."

    $null = Get-Command ruff -ErrorAction Stop
    $null = Get-Command pytest -ErrorAction Stop

    ruff check src/
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    pytest tests/ -v --cov=src --cov-fail-under=85
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "Pre-push verification passed."
