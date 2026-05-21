"""PBH v2.0 protocol compliance validation and environment checks."""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Result dict keys
_CHECK = "check"
_PASSED = "passed"
_MESSAGE = "message"

# Required AGENTS.md sections (by heading pattern)
_REQUIRED_SECTIONS = {
    "snapshot": r"#+\s*\d*\.?\s*Project\s+Snapshot",
    "quick_start": r"#+\s*\d*\.?\s*Quick\s+Start",
    "critical_rules": r"#+\s*\d*\.?\s*Critical\s+Rules",
    "file_mapping": r"#+\s*\d*\.?\s*File\s+Mapping",
    "commands": r"#+\s*\d*\.?\s*Commands",
}

# Content patterns that MUST appear in specific sections
_CRITICAL_RULES_MUST = [
    r"make\s+verify",  # make verify commit gate
    r"(self.?evaluation|自评估)",  # self-evaluation ban
    r"(secret|密钥|hardcode)",  # security ban
]

_FILE_MAPPING_MUST = [r"src/", r"tests/", r"docs/", r"tasks/", r"\.harness/"]

_COMMANDS_MUST = [r"make\s+verify", r"make\s+test", r"make\s+lint"]

_VALID_STAGES = {"init", "plan", "execute", "evaluate", "done"}


def _result(check: str, passed: bool, message: str) -> dict:
    """Create a single validation result dict."""
    return {_CHECK: check, _PASSED: passed, _MESSAGE: message}


def validate_file_existence(project_path: Path) -> list[dict]:
    """Check that required PBH files exist.

    Returns a list of result dicts for each file check.
    """
    results: list[dict] = []
    agents_md = project_path / "AGENTS.md"
    makefile = project_path / "Makefile"
    progress_json = project_path / ".harness" / "progress.json"

    results.append(_result(
        "AGENTS.md exists",
        agents_md.is_file(),
        f"{'Found' if agents_md.is_file() else 'Missing'}: {agents_md}",
    ))

    makefile_ok = makefile.is_file()
    results.append(_result(
        "Makefile exists",
        makefile_ok,
        f"{'Found' if makefile_ok else 'Missing'}: {makefile}",
    ))

    progress_ok = progress_json.is_file()
    results.append(_result(
        ".harness/progress.json exists",
        progress_ok,
        f"{'Found' if progress_ok else 'Missing'}: {progress_json}",
    ))

    return results


def _check_heading_sections(content: str) -> list[dict]:
    """Verify AGENTS.md contains all required sections."""
    results: list[dict] = []
    for name, pattern in _REQUIRED_SECTIONS.items():
        found = bool(re.search(pattern, content, re.IGNORECASE))
        results.append(_result(
            f"AGENTS.md §{name}",
            found,
            f"Section matching /{pattern}/ {'found' if found else 'NOT found'}",
        ))
    return results


def _check_section_content(content: str) -> list[dict]:
    """Verify required content within specific sections."""
    results: list[dict] = []

    # Split into sections by heading
    sections: dict[str, str] = {}
    current_name = ""
    current_lines: list[str] = []
    for line in content.splitlines():
        if re.match(r"^#+\s", line):
            if current_name:
                sections[current_name] = "\n".join(current_lines)
            current_name = line.lower()
            current_lines = [line]
        else:
            current_lines.append(line)
    if current_name:
        sections[current_name] = "\n".join(current_lines)

    # Find critical rules section
    crit_body = ""
    for sec_name, sec_body in sections.items():
        if re.search(r"critical\s+rules", sec_name, re.IGNORECASE):
            crit_body = sec_body
            break

    for pattern in _CRITICAL_RULES_MUST:
        found = bool(re.search(pattern, crit_body, re.IGNORECASE))
        results.append(_result(
            f"Critical Rules content: {pattern}",
            found,
            f"Pattern /{pattern}/ {'found' if found else 'NOT found'} in §Critical Rules",
        ))

    # Find file mapping section
    fm_body = ""
    for sec_name, sec_body in sections.items():
        if re.search(r"file\s+mapping", sec_name, re.IGNORECASE):
            fm_body = sec_body
            break

    for pattern in _FILE_MAPPING_MUST:
        found = bool(re.search(pattern, fm_body, re.IGNORECASE))
        results.append(_result(
            f"File Mapping entry: {pattern}",
            found,
            f"Pattern /{pattern}/ {'found' if found else 'NOT found'} in §File Mapping",
        ))

    # Find commands section
    cmd_body = ""
    for sec_name, sec_body in sections.items():
        if re.search(r"commands", sec_name, re.IGNORECASE):
            cmd_body = sec_body
            break

    for pattern in _COMMANDS_MUST:
        found = bool(re.search(pattern, cmd_body, re.IGNORECASE))
        results.append(_result(
            f"Commands entry: {pattern}",
            found,
            f"Pattern /{pattern}/ {'found' if found else 'NOT found'} in §Commands",
        ))

    return results


def _check_quick_start(content: str) -> list[dict]:
    """Verify Quick Start section: first step must be 'make verify'."""
    results: list[dict] = []
    # Find the quick start section
    match = re.search(
        r"#+\s*\d*\.?\s*Quick\s+Start.*?\n(.*?)(?=\n#|\Z)",
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if match:
        body = match.group(1)
        # First numbered step must mention make verify
        step_match = re.search(r"^\s*\d+\.\s*(.+)$", body, re.MULTILINE)
        if step_match:
            first_step = step_match.group(1)
            ok = bool(re.search(r"make\s+verify", first_step, re.IGNORECASE))
            results.append(_result(
                "Quick Start first step is make verify",
                ok,
                f"First step: '{first_step.strip()}'",
            ))
        else:
            results.append(_result(
                "Quick Start first step is make verify",
                False,
                "No numbered steps found in Quick Start",
            ))
    return results


def validate_agents_md(project_path: Path) -> list[dict]:
    """Validate AGENTS.md content compliance.

    Checks section structure, required content, and quick start order.
    """
    results: list[dict] = []
    agents_md = project_path / "AGENTS.md"
    if not agents_md.is_file():
        results.append(_result("AGENTS.md readable", False, "File does not exist"))
        return results

    try:
        content = agents_md.read_text(encoding="utf-8")
    except Exception as exc:
        results.append(_result("AGENTS.md readable", False, f"Read error: {exc}"))
        return results

    results.append(_result("AGENTS.md readable", True, f"Read OK ({len(content)} bytes)"))
    results.extend(_check_heading_sections(content))
    results.extend(_check_section_content(content))
    results.extend(_check_quick_start(content))

    return results


def validate_progress_json(project_path: Path) -> list[dict]:
    """Validate .harness/progress.json schema compliance."""
    results: list[dict] = []
    pj = project_path / ".harness" / "progress.json"

    if not pj.is_file():
        results.append(_result("progress.json readable", False, "File does not exist"))
        return results

    try:
        raw = pj.read_text(encoding="utf-8")
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        results.append(_result("progress.json valid JSON", False, f"JSON parse error: {exc}"))
        return results
    except Exception as exc:
        results.append(_result("progress.json readable", False, f"Read error: {exc}"))
        return results

    results.append(_result("progress.json valid JSON", True, "Parsed successfully"))

    # Check required fields
    if "project_name" in data:
        results.append(_result(
            "progress.json project_name",
            isinstance(data["project_name"], str) and len(data["project_name"]) > 0,
            f"project_name = {data.get('project_name')!r}",
        ))
    else:
        results.append(_result("progress.json project_name", False, "Missing 'project_name'"))

    if "current_stage" in data:
        ok = data["current_stage"] in _VALID_STAGES
        results.append(_result(
            "progress.json current_stage",
            ok,
            f"current_stage = {data.get('current_stage')!r}"
            + ("" if ok else f" (must be one of {_VALID_STAGES})"),
        ))
    else:
        results.append(_result("progress.json current_stage", False, "Missing 'current_stage'"))

    if "plans" in data:
        results.append(_result(
            "progress.json plans",
            isinstance(data["plans"], list),
            f"plans is {type(data['plans']).__name__} with {len(data.get('plans', []))} items",
        ))
    else:
        results.append(_result("progress.json plans", False, "Missing 'plans'"))

    if "last_updated" in data:
        # Basic ISO 8601 check
        val = data["last_updated"]
        iso_ok = isinstance(val, str) and bool(
            re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", val)
        )
        results.append(_result(
            "progress.json last_updated",
            iso_ok,
            f"last_updated = {val!r}" + ("" if iso_ok else " (not ISO 8601 format)"),
        ))
    else:
        results.append(_result("progress.json last_updated", False, "Missing 'last_updated'"))

    return results


def validate_makefile(project_path: Path) -> list[dict]:
    """Validate Makefile contains a verify target."""
    results: list[dict] = []
    makefile = project_path / "Makefile"

    if not makefile.is_file():
        results.append(_result("Makefile verify target", False, "Makefile does not exist"))
        return results

    try:
        content = makefile.read_text(encoding="utf-8")
    except Exception as exc:
        results.append(_result("Makefile readable", False, f"Read error: {exc}"))
        return results

    has_verify = bool(re.search(r"^verify\s*:", content, re.MULTILINE))
    results.append(_result(
        "Makefile verify target",
        has_verify,
        "Target 'verify:' found" if has_verify else "Target 'verify:' NOT found",
    ))

    return results


def validate_make_verify(project_path: Path) -> list[dict]:
    """Run 'make verify' and check the exit code (behavioral compliance)."""
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
    except Exception as exc:
        results.append(_result("make verify passes", False, f"Error: {exc}"))

    return results


def validate_project(project_path: str = ".") -> tuple[bool, list[dict]]:
    """Run all PBH v2.0 compliance checks on a project.

    Args:
        project_path: Path to the project root. Defaults to current directory.

    Returns:
        A tuple of (all_passed: bool, results: list[dict]).
    """
    path = Path(project_path).resolve()
    all_results: list[dict] = []

    # 1. File existence
    file_results = validate_file_existence(path)
    all_results.extend(file_results)

    # 2. Content compliance (only if files exist)
    files_ok = all(r[_PASSED] for r in file_results)
    if files_ok:
        all_results.extend(validate_agents_md(path))
        all_results.extend(validate_progress_json(path))
        all_results.extend(validate_makefile(path))

        # 3. Behavioral compliance
        content_ok = all(
            r[_PASSED] for r in all_results if r[_CHECK] != "make verify passes"
        )
        if content_ok:
            all_results.extend(validate_make_verify(path))

    all_passed = all(r[_PASSED] for r in all_results)
    return all_passed, all_results


# -- Doctor (environment check) ---------------------------------------------


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
    """Check that the local environment satisfies PBH collaboration prerequisites.

    Returns:
        A tuple of (all_ok: bool, results: list[dict]).
    """
    results: list[dict] = []
    results.append(_check_tool("make"))
    results.append(_check_tool("git"))
    results.append(_check_tool("python"))
    results.append(_check_tool("pip"))
    results.append(_check_python_version())

    all_ok = all(r[_PASSED] for r in results)
    return all_ok, results
