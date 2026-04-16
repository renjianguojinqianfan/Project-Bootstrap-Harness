"""Core logic for harness-init."""

import os
import re
import stat
import subprocess
from datetime import UTC, datetime
from pathlib import Path


def _get_templates_dir() -> Path:
    """返回模板资源目录。"""
    return Path(__file__).parent / "templates"


def _validate_project_name(project_name: str) -> None:
    """验证项目名非空且不包含非法路径字符。"""
    if not project_name or not project_name.strip():
        raise ValueError("Project name cannot be empty.")
    if any(c in project_name for c in ("/", "\\", "..")):
        raise ValueError("Project name cannot contain path separators or '..'.")
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_-]*$", project_name):
        raise ValueError(
            "Project name must start with a letter or underscore "
            "and contain only letters, digits, hyphens, and underscores."
        )


def _to_package_name(project_name: str) -> str:
    """将项目名转换为合法的 Python 包名。"""
    return project_name.replace("-", "_").lower()


def _to_pep508_name(project_name: str) -> str:
    """将项目名转换为合法的 PEP 508 标识符。"""
    sanitized = re.sub(r"[^A-Za-z0-9._-]", "-", project_name)
    sanitized = sanitized.lstrip("._-")
    if not sanitized:
        sanitized = "project"
    return sanitized


def _ensure_dir(path: Path) -> None:
    """确保目录存在。"""
    path.mkdir(parents=True, exist_ok=True)


def _is_binary(path: Path) -> bool:
    """判断文件是否为二进制文件。"""
    with open(path, "rb") as f:
        chunk = f.read(8192)
        return b"\x00" in chunk


def _copy_or_render_template(
    template_path: Path,
    output_path: Path,
    project_name: str,
    description: str = "",
    author: str = "",
    email: str = "",
) -> None:
    """渲染模板文件到目标路径；二进制文件直接复制。"""
    if _is_binary(template_path):
        import shutil

        shutil.copy2(template_path, output_path)
        return
    package_name = _to_package_name(project_name)
    pep508_name = _to_pep508_name(project_name)
    replacements = {
        "{project_name}": project_name,
        "{package_name}": package_name,
        "{pep508_name}": pep508_name,
        "{project_description}": description,
        "{author_name}": author,
        "{author_email}": email,
    }
    content = template_path.read_text(encoding="utf-8")
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    output_path.write_text(content, encoding="utf-8")


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


def _git(project_path: Path, *args: str) -> None:
    """运行 Git 命令，失败时抛出包含 stderr 的异常。"""
    result = subprocess.run(["git", *args], cwd=project_path, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")


def _init_git(project_path: Path, author: str = "", email: str = "") -> None:
    """初始化 Git 仓库并创建初始提交。"""
    _git(project_path, "init")
    _git(project_path, "config", "user.email", email or "harness-init@localhost")
    _git(project_path, "config", "user.name", author or "harness-init")
    _git(project_path, "add", ".")
    _git(project_path, "commit", "-m", "Initial commit")


def _on_remove_error(_func: object, path: str, _exc_info: object) -> None:
    """Windows 下删除只读文件时的回调。"""
    os.chmod(path, stat.S_IWRITE)
    if os.path.isdir(path) and not os.path.islink(path):
        os.rmdir(path)
    else:
        os.unlink(path)


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
    project_name = path.name
    _validate_project_name(project_name)
    if ".." in path.parts:
        raise ValueError("Project path cannot contain '..'.")
    if path.exists() and not force and (path.is_file() or any(path.iterdir())):
        raise FileExistsError(f"Directory {path} already exists and is not empty. Use --force to overwrite.")
    if force and path.exists():
        import shutil

        suffix = datetime.now(UTC).strftime(".bak-%Y%m%d%H%M%S%f")
        backup_path = path.with_name(path.name + suffix)
        shutil.move(str(path), str(backup_path))
    _create_directories(path, project_name)
    _copy_templates(path, project_name, description, author, email)
    _create_source_files(path, project_name)
    if not no_git:
        try:
            _init_git(path, author, email)
        except Exception as exc:
            import shutil

            git_dir = path / ".git"
            if git_dir.exists():
                shutil.rmtree(str(git_dir), onerror=_on_remove_error)
            raise RuntimeError(f"Git initialization failed: {exc}") from exc
