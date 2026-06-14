"""Core logic for harness-init."""

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from harness_init._git import _init_git, _on_remove_error
from harness_init._ide import _is_excluded_ide
from harness_init._quick import _is_excluded_quick
from harness_init._templates import copy_templates
from harness_init._utils import (
    _ensure_dir,
    _to_package_name,
    _validate_project_name,
)

_VALID_TEMPLATES: frozenset[str] = frozenset({"cli", "lib", "web", "notebook"})


def _validate_template(template: str) -> None:
    """Validate template type."""
    if template not in _VALID_TEMPLATES:
        raise ValueError(
            f"Unknown template '{template}'. "
            f"Valid templates: {', '.join(sorted(_VALID_TEMPLATES))}"
        )


def _get_templates_dir(template: str = "cli") -> Path:
    """Return type-specific template directory."""
    return Path(__file__).parent / "templates" / template


def _get_common_templates_dir() -> Path:
    """Return shared template directory."""
    return Path(__file__).parent / "templates" / "common"


def _create_directories(
    project_path: Path, project_name: str, quick: bool = False, template: str = "cli"
) -> None:
    """Create standard project directory structure."""
    package_name = _to_package_name(project_name)
    dirs = [
        ".github/workflows",
        ".harness/templates",
        "docs",
        "tasks",
        "tests",
    ]
    if template == "notebook":
        dirs.append("notebooks")
    else:
        dirs.append(f"src/{package_name}")
    for d in dirs:
        if quick and _is_excluded_quick(d + "/", package_name):
            continue
        _ensure_dir(project_path / d)


def _copy_templates(
    project_path: Path,
    project_name: str,
    description: str = "",
    author: str = "",
    email: str = "",
    quick: bool = False,
    template: str = "cli",
    ide: str = "all",
) -> None:
    """Copy template files into the project directory."""
    package_name = _to_package_name(project_name)

    def _is_excluded(rel_str: str) -> bool:
        if quick and _is_excluded_quick(rel_str, package_name):
            return True
        return _is_excluded_ide(rel_str, ide)

    copy_templates(
        _get_templates_dir(template),
        project_path,
        project_name,
        package_name,
        description=description,
        author=author,
        email=email,
        quick=quick,
        is_excluded=_is_excluded,
        common_dir=_get_common_templates_dir(),
    )


def _create_source_files(
    project_path: Path, project_name: str, quick: bool = False, template: str = "cli"
) -> None:
    """Create initial Python source and test files."""
    package_name = _to_package_name(project_name)
    (project_path / "tests" / "__init__.py").write_text("", encoding="utf-8")
    if template == "notebook":
        return
    pkg_dir = project_path / "src" / package_name
    (pkg_dir / "__init__.py").write_text(
        f'"""{package_name} package."""\n\n__version__ = "0.1.0"\n',
        encoding="utf-8",
    )


def _create_progress_json(project_path: Path, project_name: str) -> None:
    """Create initial .harness/progress.json with proper schema."""
    progress_data = {
        "project_name": project_name,
        "current_stage": "init",
        "plans": [],
        "last_updated": datetime.now(UTC).isoformat(),
    }
    (project_path / ".harness" / "progress.json").write_text(
        json.dumps(progress_data, indent=2),
        encoding="utf-8",
    )


def _prepare_project_path(path: Path, force: bool) -> None:
    """Validate project path and backup old directory if needed."""
    project_name = path.name
    _validate_project_name(project_name)
    if ".." in path.parts:
        raise ValueError("Project path cannot contain '..'.")
    if path.exists() and not force and (path.is_file() or any(path.iterdir())):
        raise FileExistsError(
            f"Directory {path} already exists and is not empty. Use --force to overwrite."
        )
    if force and path.exists():
        suffix = datetime.now(UTC).strftime(".bak-%Y%m%d%H%M%S%f")
        backup_path = path.with_name(path.name + suffix)
        shutil.move(str(path), str(backup_path))


def _setup_project(
    path: Path,
    project_name: str,
    description: str,
    author: str,
    email: str,
    quick: bool = False,
    template: str = "cli",
    ide: str = "all",
) -> None:
    """Create directories, copy templates and generate initial source."""
    _create_directories(path, project_name, quick=quick, template=template)
    _copy_templates(
        path, project_name, description, author, email,
        quick=quick, template=template, ide=ide,
    )
    _create_source_files(path, project_name, quick=quick, template=template)
    _create_progress_json(path, path.name)


def _init_git_safe(path: Path, author: str, email: str) -> None:
    """Safely initialize a Git repository, rolling back on failure."""
    try:
        _init_git(path, author, email)
    except Exception as exc:
        git_dir = path / ".git"
        if git_dir.exists():
            shutil.rmtree(str(git_dir), onerror=_on_remove_error)
        raise RuntimeError(f"Git initialization failed: {exc}") from exc


def init_project(
    project_path: str,
    *,
    force: bool = False,
    no_git: bool = False,
    description: str = "",
    author: str = "",
    email: str = "",
    quick: bool = False,
    template: str = "cli",
    ide: str = "all",
) -> None:
    """Initialize a new Harness Engineering project."""
    path = Path(project_path)
    _validate_template(template)
    _prepare_project_path(path, force)
    _setup_project(
        path, path.name, description, author, email,
        quick=quick, template=template, ide=ide,
    )
    if not no_git:
        _init_git_safe(path, author, email)
