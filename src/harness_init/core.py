"""Core logic for harness-init."""

import shutil
from datetime import UTC, datetime
from pathlib import Path

from harness_init._git import _init_git, _on_remove_error
from harness_init._utils import (
    _copy_or_render_template,
    _ensure_dir,
    _to_package_name,
    _validate_project_name,
)


def _get_templates_dir() -> Path:
    """返回模板资源目录。"""
    return Path(__file__).parent / "templates"


def _create_directories(project_path: Path, project_name: str) -> None:
    """创建项目标准目录结构。"""
    package_name = _to_package_name(project_name)
    dirs = [
        ".harness/plans",
        ".harness/eval_feedback",
        ".harness/state",
        ".harness/templates",
        ".harness/logs",
        "configs",
        "docs",
        "docs/decisions",
        f"src/{package_name}",
        f"src/{package_name}/harness",
        f"src/{package_name}/agents",
        f"src/{package_name}/tools",
        f"src/{package_name}/utils",
        "tests",
    ]
    for d in dirs:
        _ensure_dir(project_path / d)


_IGNORED_NAMES = {
    ".ruff_cache",
    "__pycache__",
    ".DS_Store",
    ".git",
    ".pytest_cache",
    ".mypy_cache",
}
_IGNORED_SUFFIXES = (".pyc", ".pyo", ".swp", "~")


def _should_skip(path: Path) -> bool:
    """判断模板路径是否应被跳过。"""
    if not path.is_file():
        return True
    if any(part in _IGNORED_NAMES for part in path.parts):
        return True
    return path.name.endswith(_IGNORED_SUFFIXES)


def _copy_templates(
    project_path: Path,
    project_name: str,
    description: str = "",
    author: str = "",
    email: str = "",
) -> None:
    """复制模板文件到项目目录（递归）。"""
    templates_dir = _get_templates_dir()
    package_name = _to_package_name(project_name)
    for src in templates_dir.rglob("*"):
        if _should_skip(src):
            continue
        rel = src.relative_to(templates_dir)
        rel_str = str(rel).replace("{package_name}", package_name)
        dst = project_path / rel_str
        dst.parent.mkdir(parents=True, exist_ok=True)
        _copy_or_render_template(src, dst, project_name, description, author, email)
        dst.chmod(src.stat().st_mode)


def _create_source_files(project_path: Path, project_name: str) -> None:
    """创建初始 Python 源码和测试文件。"""
    package_name = _to_package_name(project_name)
    pkg_dir = project_path / "src" / package_name
    for sub in ["harness", "agents", "tools", "utils"]:
        (pkg_dir / sub / "__init__.py").write_text("", encoding="utf-8")
    (project_path / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (pkg_dir / "__init__.py").write_text(
        f'"""{package_name} package."""\n\n__version__ = "0.1.0"\n',
        encoding="utf-8",
    )
    (project_path / ".harness" / "progress.json").write_text('{"current_plan": null, "tasks": []}', encoding="utf-8")


def _prepare_project_path(path: Path, force: bool) -> None:
    """验证项目路径，必要时备份旧目录。"""
    project_name = path.name
    _validate_project_name(project_name)
    if ".." in path.parts:
        raise ValueError("Project path cannot contain '..'.")
    if path.exists() and not force and (path.is_file() or any(path.iterdir())):
        raise FileExistsError(f"Directory {path} already exists and is not empty. Use --force to overwrite.")
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
) -> None:
    """创建目录、复制模板并生成初始源码。"""
    _create_directories(path, project_name)
    _copy_templates(path, project_name, description, author, email)
    _create_source_files(path, project_name)


def init_project(
    project_path: str,
    *,
    force: bool = False,
    no_git: bool = False,
    description: str = "",
    author: str = "",
    email: str = "",
) -> None:
    """初始化新项目。

    Args:
        project_path: 项目目标路径。
        force: 是否强制覆盖已存在目录。
        no_git: 是否跳过 Git 初始化。
        description: 项目描述。
        author: 作者名。
        email: 作者邮箱。
    """
    path = Path(project_path)
    _prepare_project_path(path, force)
    _setup_project(path, path.name, description, author, email)
    if not no_git:
        try:
            _init_git(path, author, email)
        except Exception as exc:
            git_dir = path / ".git"
            if git_dir.exists():
                shutil.rmtree(str(git_dir), onerror=_on_remove_error)
            raise RuntimeError(f"Git initialization failed: {exc}") from exc
