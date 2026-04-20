# Design: `--quick` Mode for harness-init

**Date**: 2026-04-20  
**Status**: Approved for implementation  
**Scope**: Define exclusion patterns, interface contract, and template variant mapping for `harness-init --quick`.

---

## 1. Goal

Provide a `--quick` CLI flag that generates a minimal, runnable project skeleton by excluding AI-agent-specific files, documentation, and optional infrastructure. The generated project must still pass `make verify`.

---

## 2. Exclusion Set (`_QUICK_MODE_EXCLUSIONS`)

### 2.1 Definition

Introduce a module-level constant in `core.py`:

```python
_QUICK_MODE_EXCLUSIONS: frozenset[str] = frozenset({
    # IDE / AI assistant configs
    "CLAUDE.md",
    ".cursorrules",
    
    # GitHub infrastructure
    ".github/",
    
    # Pre-commit hooks
    ".pre-commit-config.yaml",
    
    # Decision records & heavy documentation
    "docs/decisions/",
    "docs/PROJECT_MAP.md",
    "docs/context.md",
    
    # Utility scripts
    "scripts/",
    
    # Environment configs (dev/test/prod)
    "configs/",
    
    # English readme (quick mode is zh-CN first)
    "README.en.md",
    
    # OpenCode IDE config
    "opencode.yaml",
    
    # Agent subsystems (harness + agents + tools + utils)
    "src/{package_name}/agents/",
    "src/{package_name}/harness/",
    "src/{package_name}/tools/",
    "src/{package_name}/utils/",
    
    # Harness-specific tests
    "tests/test_harness.py",
})
```

### 2.2 Matching Rules

| Rule | Behavior |
|------|----------|
| Ends with `/` | Treat as **directory prefix match** — exclude any path whose relative path starts with this prefix. |
| No trailing `/` | Treat as **exact file match** — exclude only when the relative path equals this string (after `{package_name}` substitution). |
| `{package_name}` placeholder | Substituted with the computed package name **before** matching. |
| Case sensitivity | Match is case-sensitive (same as filesystem on target platform). |

### 2.3 Edge Cases

| Scenario | Resolution |
|----------|------------|
| Template has both `AGENTS.md` and `AGENTS.quick.md` | Only `AGENTS.quick.md` is processed (via variant mapping); `AGENTS.md` is excluded because `AGENTS.md` itself is **not** in the exclusion list, but the quick variant **replaces** it. See §3. |
| Template has `docs/decisions/ADR_TEMPLATE.md` but no `docs/decisions/` directory otherwise | Still excluded because `docs/decisions/` is a directory prefix match. |
| `src/{package_name}/agents/__init__.py` created by `_create_source_files()` | Skipped when `quick=True` via conditional logic in `_create_source_files()`. |
| Empty directory left after exclusion | Acceptable; Python's `pathlib` mkdir parents will create whatever remains. |

---

## 3. Template Variant Mapping (`.quick.` Files)

### 3.1 Mapping Table

| Template Source (in `templates/`) | Generated Target | Condition |
|-----------------------------------|------------------|-----------|
| `AGENTS.quick.md` | `AGENTS.md` | `quick=True` only |
| `pyproject.quick.toml` | `pyproject.toml` | `quick=True` only |
| `src/{package_name}/cli.quick.py` | `src/{package_name}/cli.py` | `quick=True` only |
| `tests/test_cli.quick.py` | `tests/test_cli.py` | `quick=True` only |

### 3.2 Fallback Rules

| Scenario | Behavior |
|----------|----------|
| `quick=True` and `.quick.` variant exists | Use `.quick.` variant, skip base file. |
| `quick=True` and `.quick.` variant **missing** | Fall back to base file (if not in exclusion set). |
| `quick=False` (default) | Ignore all `.quick.` variants; use base files normally. |
| Both `AGENTS.md` and `AGENTS.quick.md` present, `quick=True` | Generate `AGENTS.md` from `AGENTS.quick.md`; do **not** copy `AGENTS.md`. |

### 3.3 Naming Convention

The variant suffix is **`.quick.`** inserted before the final extension:

- `AGENTS.quick.md` → `AGENTS.md`
- `pyproject.quick.toml` → `pyproject.toml`
- `cli.quick.py` → `cli.py`
- `test_cli.quick.py` → `test_cli.py`

This is unambiguous and avoids ambiguity with multi-dot filenames.

---

## 4. Interface Contract (Function Signatures)

### 4.1 New Parameter

Add `quick: bool = False` to the following functions in `core.py`:

```python
def init_project(
    project_path: str,
    *,
    force: bool = False,
    no_git: bool = False,
    description: str = "",
    author: str = "",
    email: str = "",
    quick: bool = False,  # ← NEW
) -> None:
    ...


def _setup_project(
    path: Path,
    project_name: str,
    description: str,
    author: str,
    email: str,
    quick: bool = False,  # ← NEW
) -> None:
    ...


def _create_directories(
    project_path: Path,
    project_name: str,
    quick: bool = False,  # ← NEW
) -> None:
    ...


def _copy_templates(
    project_path: Path,
    project_name: str,
    description: str = "",
    author: str = "",
    email: str = "",
    quick: bool = False,  # ← NEW
) -> None:
    ...


def _create_source_files(
    project_path: Path,
    project_name: str,
    quick: bool = False,  # ← NEW
) -> None:
    ...
```

### 4.2 CLI Parameter

Add to `cli.py`:

```python
def _run_init(
    project_name: str,
    force: bool = False,
    no_git: bool = False,
    description: str = "",
    author: str = "",
    email: str = "",
    quick: bool = False,  # ← NEW
) -> None:
    ...


def main(
    project_name: str = typer.Argument(..., help="项目名称或目标路径。"),
    force: bool = typer.Option(False, "--force", "-f", help="强制覆盖已存在目录。"),
    no_git: bool = typer.Option(False, "--no-git", help="跳过 Git 初始化。"),
    version: bool = typer.Option(...),
    yes: bool = typer.Option(False, "--yes", "-y", help="跳过交互提示，使用默认值。"),
    quick: bool = typer.Option(False, "--quick", "-q", help="快速模式：生成最小可运行项目。"),  # ← NEW
) -> None:
    ...
```

### 4.3 Backward Compatibility

- Default value is `False` for all new parameters.
- Existing keyword-only call sites (e.g., `init_project("foo", force=True)`) remain valid.
- Positional calls are unaffected because `quick` is keyword-only in `init_project` and placed after existing args in internal functions.

---

## 5. Conditional Logic by Function

### 5.1 `_create_directories(project_path, project_name, quick=False)`

```text
IF quick = True:
    Skip creating any directory whose relative path matches a directory-prefix entry in _QUICK_MODE_EXCLUSIONS
ELSE:
    Create all directories (existing behavior)
```

**Affected directories** (removed in quick mode):
- `.github/workflows`
- `configs`
- `docs/decisions`
- `scripts`
- `src/{package_name}/harness`
- `src/{package_name}/agents`
- `src/{package_name}/tools`
- `src/{package_name}/utils`

**Kept directories**:
- `.harness/*`
- `docs` (but not `docs/decisions/`)
- `src/{package_name}`
- `tests`

### 5.2 `_copy_templates(project_path, project_name, ..., quick=False)`

```text
FOR each file in templates/ (recursive):
    1. Apply _should_skip() filter (unchanged)
    2. Compute relative path, substituting {package_name}
    3. IF quick = True AND rel_path matches _QUICK_MODE_EXCLUSIONS:
           CONTINUE (skip)
    4. IF file has .quick. suffix:
           IF quick = True:
               Use as source, strip .quick. for destination
           ELSE:
               CONTINUE (ignore .quick. variants in normal mode)
    5. IF quick = True AND base file has a .quick. variant that was processed:
           CONTINUE (skip base file)
    6. Copy / render as usual
```

**Key detail**: The `.quick.` variant check must happen **before** the exclusion check, because a `.quick.` file's base name might be in the exclusion set (e.g., `AGENTS.md` is not excluded, but if it were, we'd still want to process `AGENTS.quick.md`).

### 5.3 `_create_source_files(project_path, project_name, quick=False)`

```text
package_name = _to_package_name(project_name)
pkg_dir = project_path / "src" / package_name

IF quick = False:
    FOR sub in ["harness", "agents", "tools", "utils"]:
        (pkg_dir / sub / "__init__.py").write_text("")
ELSE:
    # Skip agent subsystems entirely
    PASS

# Always create these:
(project_path / "tests" / "__init__.py").write_text("")
(pkg_dir / "__init__.py").write_text(f'"""{package_name} package."""\n\n__version__ = "0.1.0"\n')
```

---

## 6. Expected Directory Structure (`--quick` vs Default)

### Default Mode

```
my-project/
├── .harness/
│   ├── plans/
│   ├── eval_feedback/
│   ├── state/
│   ├── templates/
│   └── logs/
├── configs/                  # ← excluded in quick
├── docs/
│   └── decisions/            # ← excluded in quick
├── scripts/                  # ← excluded in quick
├── src/my_project/
│   ├── cli.py
│   ├── harness/              # ← excluded in quick
│   ├── agents/               # ← excluded in quick
│   ├── tools/                # ← excluded in quick
│   └── utils/                # ← excluded in quick
├── tests/
├── .github/                  # ← excluded in quick
├── AGENTS.md
├── Makefile
├── pyproject.toml
├── README.md
├── README.en.md              # ← excluded in quick
└── ...
```

### Quick Mode

```
my-project/
├── .harness/
│   ├── plans/
│   ├── eval_feedback/
│   ├── state/
│   ├── templates/
│   └── logs/
├── docs/                     # kept, but empty (no decisions/)
├── src/my_project/
│   ├── cli.py                # from cli.quick.py
│   └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_cli.py           # from test_cli.quick.py
├── Makefile
├── pyproject.toml            # from pyproject.quick.toml
├── README.md
└── ...
```

---

## 7. Testing Requirements (for Implementation Phase)

1. **Unit test**: `_is_excluded_quick(rel_path, package_name)` returns `True` for all entries in `_QUICK_MODE_EXCLUSIONS`.
2. **Unit test**: `_resolve_template_variant("AGENTS.quick.md", quick=True)` returns `"AGENTS.md"`; `quick=False` returns `None`.
3. **Integration test**: `init_project("test_quick", quick=True)` generates a directory tree with no excluded paths.
4. **Integration test**: `init_project("test_quick", quick=True)` followed by `make verify` passes.
5. **Regression test**: `init_project("test_default")` (default `quick=False`) produces identical output to before this change.

---

## 8. Open Questions / Future Considerations

| Question | Recommendation |
|----------|----------------|
| Should `--quick` also skip `make verify` hooks? | No; quick mode should still pass verification. The goal is smaller footprint, not lower quality. |
| Should `.harness/` be excluded too? | No; progress tracking and plan templates are core to the scaffold's value proposition. |
| Should there be a `--quick` config in `pyproject.quick.toml`? | Yes; the quick variant should have fewer dev dependencies (no pre-commit, etc.). |

---

## 9. Decision Log

| Decision | Rationale |
|----------|-----------|
| Use `.quick.` infix (not suffix) | `AGENTS.quick.md` → `AGENTS.md` is unambiguous; suffix like `AGENTS.md.quick` would be confusing. |
| Exclude `README.en.md` but keep `README.md` | Quick mode targets Chinese users by default; English readme is optional overhead. |
| Exclude entire `src/{pkg}/agents/` etc. | These are AI-agent subsystems; quick mode is for human-only projects. |
| Keep `.harness/` in quick mode | The harness state/progress system is lightweight and defines the project's workflow identity. |
| Directory exclusions use trailing `/` | Matches `os.path` conventions and is visually distinct from file exclusions. |

---

*End of Design Document*
