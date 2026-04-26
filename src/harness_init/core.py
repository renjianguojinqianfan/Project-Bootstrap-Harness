"""Core logic for harness-init."""

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from harness_init._git import _init_git, _on_remove_error
from harness_init._templates import copy_templates
from harness_init._utils import (
    _ensure_dir,
    _to_package_name,
    _validate_project_name,
)

_VALID_TEMPLATES: frozenset[str] = frozenset({"cli", "lib", "web", "notebook"})

_IDE_FILE_MAP: dict[str, str] = {
    "cursor": ".cursorrules",
    "claude": "CLAUDE.md",
    "trae": ".trae/",
    "copilot": ".github/copilot-instructions.md",
    "opencode": "opencode.yaml",
}

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


def _validate_template(template: str) -> None:
    """验证模板类型是否有效。"""
    if template not in _VALID_TEMPLATES:
        raise ValueError(
            f"Unknown template '{template}'. "
            f"Valid templates: {', '.join(sorted(_VALID_TEMPLATES))}"
        )


def _get_templates_dir(template: str = "cli") -> Path:
    """返回类型特定模板目录。"""
    return Path(__file__).parent / "templates" / template


def _get_common_templates_dir() -> Path:
    """返回共享模板目录。"""
    return Path(__file__).parent / "templates" / "common"


def _is_ide_file(rel_path: str) -> bool:
    """检查路径是否匹配任何 IDE 配置文件模式。"""
    for pattern in _IDE_FILE_MAP.values():
        if pattern.endswith("/"):
            if rel_path.startswith(pattern) or rel_path.startswith(pattern.rstrip("/")):
                return True
        else:
            if rel_path == pattern:
                return True
    return False


def _is_excluded_ide(rel_path: str, ide: str) -> bool:
    """如果文件是 IDE 配置且不被当前 ide 模式保留，返回 True。"""
    if ide == "all":
        return False
    if ide == "none":
        return _is_ide_file(rel_path)
    if ide in _IDE_FILE_MAP:
        target = _IDE_FILE_MAP[ide]
        if target.endswith("/"):
            if rel_path.startswith(target) or rel_path.startswith(target.rstrip("/")):
                return False
        else:
            if rel_path == target:
                return False
        return _is_ide_file(rel_path)
    return False


def _is_excluded_quick(rel_path: str, package_name: str) -> bool:
    """判断相对路径是否在 quick 模式下被排除。"""
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


def _create_directories(project_path: Path, project_name: str, quick: bool = False, template: str = "cli") -> None:
    """创建项目标准目录结构。"""
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
    """复制模板文件到项目目录（递归）。"""
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


def _create_source_files(project_path: Path, project_name: str, quick: bool = False, template: str = "cli") -> None:
    """创建初始 Python 源码和测试文件。"""
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
    """验证项目路径，必要时备份旧目录。"""
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
    """创建目录、复制模板并生成初始源码。"""
    _create_directories(path, project_name, quick=quick, template=template)
    _copy_templates(path, project_name, description, author, email, quick=quick, template=template, ide=ide)
    _create_source_files(path, project_name, quick=quick, template=template)
    _create_progress_json(path, path.name)


def _init_git_safe(path: Path, author: str, email: str) -> None:
    """安全地初始化 Git 仓库，失败时回滚。"""
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
    """初始化新项目。

    Args:
        project_path: 项目目标路径。
        force: 是否强制覆盖已存在目录。
        no_git: 是否跳过 Git 初始化。
        description: 项目描述。
        author: 作者名。
        email: 作者邮箱。
        quick: 是否使用快速模式生成最小项目。
        template: 项目模板类型（cli, lib, web, notebook）。
        ide: IDE 配置模式（all, none, cursor, claude, trae, copilot, opencode）。
    """
    path = Path(project_path)
    _validate_template(template)
    _prepare_project_path(path, force)
    _setup_project(path, path.name, description, author, email, quick=quick, template=template, ide=ide)
    if not no_git:
        _init_git_safe(path, author, email)
