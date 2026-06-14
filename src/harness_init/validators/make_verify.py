"""Behavioral compliance: run 'make verify' on the project."""

import subprocess
from pathlib import Path

from harness_init.validators._base import _result


def validate_make_verify(project_path: Path) -> list[dict]:
    """Run 'make verify' and check the exit code."""
    results: list[dict] = []
    if not (project_path / "Makefile").is_file():
        results.append(_result("make verify passes", False, "No Makefile found"))
        return results

    try:
        proc = subprocess.run(
            ["make", "verify"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=120,
        )
        ok = proc.returncode == 0
        detail = proc.stdout[-500:] + proc.stderr[-500:] if not ok else "Exit code 0"
        results.append(_result("make verify passes", ok, detail.strip()))
    except FileNotFoundError:
        results.append(_result("make verify passes", False, "'make' command not found"))
    except subprocess.TimeoutExpired:
        results.append(_result("make verify passes", False, "Timed out after 120s"))
    except OSError as exc:
        results.append(_result("make verify passes", False, f"Error: {exc}"))
    return results
