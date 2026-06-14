"""Quick-mode exclusion logic."""

_QUICK_MODE_EXCLUSIONS: frozenset[str] = frozenset(
    {
        "CLAUDE.md",
        ".cursorrules",
        "opencode.yaml",
        ".github/",
        ".pre-commit-config.yaml",
        "docs/decisions/",
        "docs/PROJECT_MAP.md",
        "docs/context.md",
        "scripts/",
        "configs/",
        "README.en.md",
        "tests/test_harness.py",
    }
)


def _is_excluded_quick(rel_path: str, package_name: str) -> bool:
    """Return True if the relative path is excluded in quick mode."""
    substituted = rel_path.replace("{package_name}", package_name)
    for exclusion in _QUICK_MODE_EXCLUSIONS:
        exc = exclusion.replace("{package_name}", package_name)
        if exc.endswith("/"):
            if substituted.startswith(exc) or substituted + "/" == exc:
                return True
        else:
            if substituted == exc:
                return True
    return False
