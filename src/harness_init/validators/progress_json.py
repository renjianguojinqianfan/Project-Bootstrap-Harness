"""progress.json schema compliance validation."""

import json
import re
from pathlib import Path
from typing import Any

from harness_init.validators._base import _VALID_STAGES, _result


def _parse_progress_json(path: Path) -> tuple[bool, Any]:
    """Try to parse progress.json; return (ok, data_or_error_message)."""
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return False, f"JSON parse error: {exc}"
    except OSError as exc:
        return False, f"Read error: {exc}"
    return True, data


def _check_project_name(data: dict) -> dict:
    """Validate progress.json project_name field."""
    if "project_name" not in data:
        return _result("progress.json project_name", False, "Missing 'project_name'")
    value = data["project_name"]
    ok = isinstance(value, str) and len(value) > 0
    return _result("progress.json project_name", ok, f"project_name = {value!r}")


def _check_current_stage(data: dict) -> dict:
    """Validate progress.json current_stage field."""
    if "current_stage" not in data:
        return _result("progress.json current_stage", False, "Missing 'current_stage'")
    value = data["current_stage"]
    ok = value in _VALID_STAGES
    msg = f"current_stage = {value!r}"
    if not ok:
        msg += f" (must be one of {_VALID_STAGES})"
    return _result("progress.json current_stage", ok, msg)


def _check_plans(data: dict) -> dict:
    """Validate progress.json plans field."""
    if "plans" not in data:
        return _result("progress.json plans", False, "Missing 'plans'")
    value = data["plans"]
    ok = isinstance(value, list)
    return _result(
        "progress.json plans",
        ok,
        f"plans is {type(value).__name__} with {len(value)} items",
    )


def _check_last_updated(data: dict) -> dict:
    """Validate progress.json last_updated field."""
    if "last_updated" not in data:
        return _result("progress.json last_updated", False, "Missing 'last_updated'")
    value = data["last_updated"]
    iso_ok = isinstance(value, str) and bool(
        re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", value)
    )
    msg = f"last_updated = {value!r}"
    if not iso_ok:
        msg += " (not ISO 8601 format)"
    return _result("progress.json last_updated", iso_ok, msg)


def validate_progress_json(project_path: Path) -> list[dict]:
    """Validate .harness/progress.json schema compliance."""
    results: list[dict] = []
    pj = project_path / ".harness" / "progress.json"

    if not pj.is_file():
        results.append(_result("progress.json readable", False, "File does not exist"))
        return results

    ok, payload = _parse_progress_json(pj)
    if not ok:
        results.append(_result("progress.json valid JSON", False, payload))
        return results

    results.append(_result("progress.json valid JSON", True, "Parsed successfully"))
    results.extend([
        _check_project_name(payload),
        _check_current_stage(payload),
        _check_plans(payload),
        _check_last_updated(payload),
    ])
    return results
