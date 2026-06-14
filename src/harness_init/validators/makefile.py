"""Makefile compliance validation."""

import re
from pathlib import Path

from harness_init.validators._base import _result


def validate_makefile(project_path: Path) -> list[dict]:
    """Validate Makefile contains a verify target."""
    results: list[dict] = []
    makefile = project_path / "Makefile"

    if not makefile.is_file():
        results.append(_result(
            "Makefile verify target", False, "Makefile does not exist"
        ))
        return results

    try:
        content = makefile.read_text(encoding="utf-8")
    except OSError as exc:
        results.append(_result("Makefile readable", False, f"Read error: {exc}"))
        return results

    has_verify = bool(re.search(r"^verify\s*:", content, re.MULTILINE))
    results.append(_result(
        "Makefile verify target",
        has_verify,
        "Target 'verify:' found" if has_verify else "Target 'verify:' NOT found",
    ))
    return results
