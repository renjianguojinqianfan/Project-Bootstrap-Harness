"""Core logic for harness-init."""

import re
import subprocess
from pathlib import Path


def _get_templates_dir() -> Path:
    """返回模板资源目录。"""
    return Path(__file__).parent / "templates"


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


def _render_template(template_path: Path, output_path: Path, project_name: str) -> None:
    """渲染模板文件到目标路径。"""
    package_name = _to_package_name(project_name)
    pep508_name = _to_pep508_name(project_name)
    content = template_path.read_text(encoding="utf-8")
    content = content.replace("{project_name}", project_name)
    content = content.replace("{package_name}", package_name)
    content = content.replace("{pep508_name}", pep508_name)
    output_path.write_text(content, encoding="utf-8")


def _create_directories(project_path: Path, project_name: str) -> None:
    """创建项目标准目录结构。"""
    package_name = _to_package_name(project_name)
    dirs = [
        ".agent/plans",
        "specs",
        f"src/{package_name}",
        "tests",
    ]
    for d in dirs:
        _ensure_dir(project_path / d)


def _copy_templates(project_path: Path, project_name: str) -> None:
    """复制模板文件到项目目录。"""
    templates_dir = _get_templates_dir()
    files = {
        "AGENTS.md": "AGENTS.md",
        "Makefile": "Makefile",
        ".gitignore": ".gitignore",
        "opencode.yaml": "opencode.yaml",
        "pyproject.toml": "pyproject.toml",
        "README.md": "README.md",
    }
    for src_name, dst_name in files.items():
        src = templates_dir / src_name
        dst = project_path / dst_name
        if src.exists():
            _render_template(src, dst, project_name)


def _create_source_files(project_path: Path, project_name: str) -> None:
    """创建初始 Python 源码和测试文件。"""
    package_name = _to_package_name(project_name)
    src_dir = project_path / "src" / package_name

    init_file = src_dir / "__init__.py"
    init_file.write_text(f'"""{package_name} package."""\n\n__version__ = "0.1.0"\n', encoding="utf-8")

    cli_file = src_dir / "cli.py"
    cli_content = f'"""CLI entry for {package_name}."""\n\nimport typer\n\napp = typer.Typer()\n\n\n@app.command()\ndef hello() -\u003e None:\n    """Say hello."""\n    typer.echo("Hello from {project_name}!")\n\n\ndef cli() -\u003e None:\n    """CLI entry point."""\n    app()\n\n\nif __name__ == "__main__":\n    cli()\n'
    cli_file.write_text(cli_content, encoding="utf-8")

    tests_dir = project_path / "tests"
    (tests_dir / "__init__.py").write_text("", encoding="utf-8")

    test_file = tests_dir / "test_cli.py"
    test_content = (
        f'"""Tests for cli.py."""\n\n'
        f"import runpy\n"
        f"import sys\n"
        f"from unittest.mock import patch\n\n"
        f"from typer.testing import CliRunner\n\n"
        f"from {package_name}.cli import app, cli\n\n"
        f"runner = CliRunner()\n\n\n"
        f"def test_hello() -\u003e None:\n"
        f'    """hello 命令应输出问候语。"""\n'
        f"    result = runner.invoke(app)\n"
        f"    assert result.exit_code == 0\n"
        f'    assert "Hello from {project_name}!" in result.output\n\n\n'
        f"def test_cli_without_args() -\u003e None:\n"
        f'    """cli 不带参数时应正常执行并退出。"""\n'
        f'    with patch.object(sys, "argv", [sys.executable]):\n'
        f"        try:\n"
        f"            cli()\n"
        f"        except SystemExit as exc:\n"
        f"            assert exc.code == 0\n\n\n"
        f"def test_cli_main_block() -\u003e None:\n"
        f'    """覆盖 if __name__ == "__main__" 分支。"""\n'
        f'    with patch.object(sys, "argv", ["{project_name}"]):\n'
        f"        try:\n"
        f'            runpy.run_module("{package_name}.cli", run_name="__main__")\n'
        f"        except SystemExit as exc:\n"
        f"            assert exc.code == 0\n"
    )
    test_file.write_text(test_content, encoding="utf-8")


def _init_git(project_path: Path) -> None:
    """初始化 Git 仓库并创建初始提交。"""
    subprocess.run(
        ["git", "init"],
        cwd=project_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "add", "."],
        cwd=project_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=project_path,
        check=True,
        capture_output=True,
    )


def init_project(project_path: str) -> None:
    """初始化新项目。

    Args:
        project_path: 项目目标路径。
    """
    path = Path(project_path)
    project_name = path.name
    _create_directories(path, project_name)
    _copy_templates(path, project_name)
    _create_source_files(path, project_name)
    _init_git(path)
