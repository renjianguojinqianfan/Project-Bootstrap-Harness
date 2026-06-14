"""IDE adapter file filtering logic."""

_IDE_FILE_MAP: dict[str, str] = {
    "cursor": ".cursorrules",
    "claude": "CLAUDE.md",
    "trae": ".trae/",
    "copilot": ".github/copilot-instructions.md",
    "opencode": "opencode.yaml",
}


def _is_ide_file(rel_path: str) -> bool:
    """Check if a path matches any IDE adapter file pattern."""
    for pattern in _IDE_FILE_MAP.values():
        if pattern.endswith("/"):
            if rel_path.startswith(pattern) or rel_path.startswith(pattern.rstrip("/")):
                return True
        else:
            if rel_path == pattern:
                return True
    return False


def _is_excluded_ide(rel_path: str, ide: str) -> bool:
    """Return True if the path is an IDE file not kept by the current ide mode."""
    if ide == "all":
        return False
    if ide == "none":
        return _is_ide_file(rel_path)
    if ide not in _IDE_FILE_MAP:
        return False
    target = _IDE_FILE_MAP[ide]
    if target.endswith("/"):
        if rel_path.startswith(target) or rel_path.startswith(target.rstrip("/")):
            return False
    else:
        if rel_path == target:
            return False
    return _is_ide_file(rel_path)
