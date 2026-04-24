"""Utility helpers for harness-init."""

import re
from datetime import UTC, datetime
from pathlib import Path


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
        return b"\x00" in f.read(8192)


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
        "{author_name}": author or "harness-init",
        "{author_email}": email or "harness-init@example.com",
        "{project_type}": "cli",
        "{generated_date}": datetime.now(UTC).strftime("%Y-%m-%d"),
    }
    content = template_path.read_text(encoding="utf-8")
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    output_path.write_text(content, encoding="utf-8")
