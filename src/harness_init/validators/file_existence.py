"""File existence validation."""

from pathlib import Path

from harness_init.validators._base import _result


def _check_required_file(results: list[dict], path: Path, label: str) -> None:
    """Append a result for a required file."""
    exists = path.is_file()
    results.append(_result(
        f"{label} exists",
        exists,
        f"{'Found' if exists else 'Missing'}: {path}",
    ))


def validate_file_existence(project_path: Path) -> list[dict]:
    """Check that required PBH files exist."""
    results: list[dict] = []
    _check_required_file(results, project_path / "AGENTS.md", "AGENTS.md")
    _check_required_file(results, project_path / "Makefile", "Makefile")
    _check_required_file(
        results,
        project_path / ".harness" / "progress.json",
        ".harness/progress.json",
    )
    return results
