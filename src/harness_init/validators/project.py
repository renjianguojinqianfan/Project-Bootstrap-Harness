"""Orchestrate all PBH v2.0 compliance checks."""

from pathlib import Path

from harness_init.validators._base import _PASSED, ValidationResult
from harness_init.validators.agents_md import validate_agents_md
from harness_init.validators.file_existence import validate_file_existence
from harness_init.validators.make_verify import validate_make_verify
from harness_init.validators.makefile import validate_makefile
from harness_init.validators.progress_json import validate_progress_json


def _all_passed(results: list[ValidationResult]) -> bool:
    """Return True if every result in the list passed."""
    return all(r[_PASSED] for r in results)


def _run_content_checks(path: Path) -> list[ValidationResult]:
    """Run content compliance checks on an existing project."""
    results: list[ValidationResult] = []
    results.extend(validate_agents_md(path))
    results.extend(validate_progress_json(path))
    results.extend(validate_makefile(path))
    return results


def validate_project(project_path: str = ".") -> tuple[bool, list[ValidationResult]]:
    """Run all PBH v2.0 compliance checks on a project."""
    path = Path(project_path).resolve()
    all_results: list[ValidationResult] = validate_file_existence(path)

    if _all_passed(all_results):
        all_results.extend(_run_content_checks(path))
        if _all_passed(all_results):
            all_results.extend(validate_make_verify(path))

    return _all_passed(all_results), all_results
