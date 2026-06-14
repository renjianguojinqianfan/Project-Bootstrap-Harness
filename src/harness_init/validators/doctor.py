"""Environment checks for PBH collaboration prerequisites."""

import shutil
import sys

from harness_init.validators._base import _result


def _check_tool(name: str, cmd: str | None = None) -> dict:
    """Check whether a CLI tool is available on PATH."""
    cmd = cmd or name
    path = shutil.which(cmd)
    if path:
        return _result(f"{name} available", True, f"Found at {path}")
    return _result(f"{name} available", False, f"'{cmd}' not found on PATH")


def _check_python_version() -> dict:
    """Check Python version >= 3.11."""
    v = sys.version_info
    ok = (v.major, v.minor) >= (3, 11)
    ver_str = f"{v.major}.{v.minor}.{v.micro}"
    return _result(
        "python >= 3.11",
        ok,
        f"Python {ver_str}" + ("" if ok else " (requires >= 3.11)"),
    )


def check_doctor() -> tuple[bool, list[dict]]:
    """Check that the local environment satisfies PBH prerequisites."""
    results: list[dict] = [
        _check_tool("make"),
        _check_tool("git"),
        _check_tool("python"),
        _check_tool("pip"),
        _check_python_version(),
    ]
    all_ok = all(r["passed"] for r in results)
    return all_ok, results
