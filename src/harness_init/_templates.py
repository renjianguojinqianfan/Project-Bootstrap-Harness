"""Template rendering and copying logic."""

import os
from collections.abc import Callable
from pathlib import Path

from harness_init._utils import _copy_or_render_template

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


def _gather_quick_bases(templates_dir: Path) -> set[str]:
    """预扫描 .quick. 变体，确定哪些基础文件需要跳过。"""
    quick_bases: set[str] = set()
    for src in templates_dir.rglob("*"):
        if _should_skip(src):
            continue
        if ".quick." in src.name:
            base_rel = src.relative_to(templates_dir)
            base_name = base_rel.name.replace(".quick.", ".")
            base_path = base_rel.parent / base_name
            quick_bases.add(str(base_path).replace("\\", "/"))
    return quick_bases


def _resolve_quick_variant(
    src: Path, rel: Path, quick: bool, quick_bases: set[str]
) -> Path | None:
    """处理 .quick. 模板变体，返回目标相对路径或 None（跳过）。"""
    if ".quick." in src.name:
        if not quick:
            return None
        dest_name = rel.name.replace(".quick.", ".")
        return rel.parent / dest_name
    if quick and str(rel).replace("\\", "/") in quick_bases:
        return None
    return rel


def _copy_template_source(
    source_dir: Path,
    project_path: Path,
    project_name: str,
    package_name: str,
    quick: bool,
    is_excluded: Callable[[str], bool] | None,
    description: str,
    author: str,
    email: str,
    quick_bases: set[str] | None = None,
) -> None:
    """从单个模板源目录复制文件。"""
    if quick_bases is None:
        quick_bases = _gather_quick_bases(source_dir)

    for src in source_dir.rglob("*"):
        if _should_skip(src):
            continue

        rel = src.relative_to(source_dir)
        resolved = _resolve_quick_variant(src, rel, quick, quick_bases)
        if resolved is None:
            continue

        rel_str = str(resolved).replace("\\", "/").replace("{package_name}", package_name)
        if is_excluded is not None and is_excluded(rel_str):
            continue

        dst = project_path / rel_str
        dst.parent.mkdir(parents=True, exist_ok=True)
        _copy_or_render_template(src, dst, project_name, description, author, email)
        dst.chmod(src.stat().st_mode)
        if dst.suffix == ".sh" and os.name != "nt":
            dst.chmod(0o755)


def copy_templates(
    templates_dir: Path,
    project_path: Path,
    project_name: str,
    package_name: str,
    *,
    description: str = "",
    author: str = "",
    email: str = "",
    quick: bool = False,
    is_excluded: Callable[[str], bool] | None = None,
    common_dir: Path | None = None,
) -> None:
    """复制模板文件到项目目录（递归）。先复制 common，再复制 type-specific。"""
    if common_dir is not None:
        _copy_template_source(
            common_dir, project_path, project_name, package_name,
            quick, is_excluded, description, author, email,
        )
    _copy_template_source(
        templates_dir, project_path, project_name, package_name,
        quick, is_excluded, description, author, email,
    )
