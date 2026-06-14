"""AGENTS.md content compliance validation."""

import re
from pathlib import Path

from harness_init.validators._base import (
    _COMMANDS_MUST,
    _CRITICAL_RULES_MUST,
    _FILE_MAPPING_MUST,
    _REQUIRED_SECTIONS,
    _result,
)


def _split_into_sections(content: str) -> dict[str, str]:
    """Split markdown content into sections keyed by heading line."""
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
    return sections


def _find_section_body(sections: dict[str, str], pattern: str) -> str:
    """Return the first section body whose name matches pattern."""
    for sec_name, sec_body in sections.items():
        if re.search(pattern, sec_name, re.IGNORECASE):
            return sec_body
    return ""


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


def _check_required_patterns(
    body: str, patterns: list[str], label: str
) -> list[dict]:
    """Verify a list of regex patterns appear in a section body."""
    results: list[dict] = []
    for pattern in patterns:
        found = bool(re.search(pattern, body, re.IGNORECASE))
        results.append(_result(
            f"{label}: {pattern}",
            found,
            f"Pattern /{pattern}/ {'found' if found else 'NOT found'}",
        ))
    return results


def _check_section_content(content: str) -> list[dict]:
    """Verify required content within specific sections."""
    sections = _split_into_sections(content)
    results: list[dict] = []
    results.extend(_check_required_patterns(
        _find_section_body(sections, r"critical\s+rules"),
        _CRITICAL_RULES_MUST,
        "Critical Rules content",
    ))
    results.extend(_check_required_patterns(
        _find_section_body(sections, r"file\s+mapping"),
        _FILE_MAPPING_MUST,
        "File Mapping entry",
    ))
    results.extend(_check_required_patterns(
        _find_section_body(sections, r"commands"),
        _COMMANDS_MUST,
        "Commands entry",
    ))
    return results


def _check_quick_start(content: str) -> list[dict]:
    """Verify Quick Start section: first step must be 'make verify'."""
    results: list[dict] = []
    match = re.search(
        r"#+\s*\d*\.?\s*Quick\s+Start.*?\n(.*?)(?=\n#|\Z)",
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return results
    body = match.group(1)
    step_match = re.search(r"^\s*\d+\.\s*(.+)$", body, re.MULTILINE)
    if not step_match:
        results.append(_result(
            "Quick Start first step is make verify",
            False,
            "No numbered steps found in Quick Start",
        ))
        return results
    first_step = step_match.group(1)
    ok = bool(re.search(r"make\s+verify", first_step, re.IGNORECASE))
    results.append(_result(
        "Quick Start first step is make verify",
        ok,
        f"First step: '{first_step.strip()}'",
    ))
    return results


def validate_agents_md(project_path: Path) -> list[dict]:
    """Validate AGENTS.md content compliance."""
    results: list[dict] = []
    agents_md = project_path / "AGENTS.md"
    if not agents_md.is_file():
        results.append(_result("AGENTS.md readable", False, "File does not exist"))
        return results

    try:
        content = agents_md.read_text(encoding="utf-8")
    except OSError as exc:
        results.append(_result("AGENTS.md readable", False, f"Read error: {exc}"))
        return results

    results.append(_result(
        "AGENTS.md readable", True, f"Read OK ({len(content)} bytes)"
    ))
    results.extend(_check_heading_sections(content))
    results.extend(_check_section_content(content))
    results.extend(_check_quick_start(content))
    return results
