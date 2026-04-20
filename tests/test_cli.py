"""Tests for cli.py."""

from pathlib import Path
from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from harness_init.cli import cli, main

runner = CliRunner()


def test_main_creates_project(tmp_path: Path) -> None:
    """应能根据项目名创建完整的 Harness v2 项目。"""
    app = typer.Typer()
    app.command()(main)
    project_path = tmp_path / "my-project"
    result = runner.invoke(app, [str(project_path)], input="\n\n\n")
    assert result.exit_code == 0
    assert project_path.is_dir()
    assert (project_path / ".git").is_dir()
    assert (project_path / ".harness" / "plans").is_dir()
    assert (project_path / "src" / "my_project" / "harness" / "runner.py").exists()
    assert (project_path / "docs" / "context.md").exists()


def test_cli_without_args_exits(tmp_path: Path) -> None:
    """不带参数时应退出并显示用法信息。"""
    with patch("sys.argv", ["harness-init"]):
        with pytest.raises(SystemExit) as exc_info:
            cli()
        assert exc_info.value.code != 0


def test_cli_version_flag() -> None:
    """--version 应显示版本号。"""
    app = typer.Typer()
    app.command()(main)
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "harness-init" in result.output


def test_cli_no_git_flag(tmp_path: Path) -> None:
    """--no-git 应跳过 Git 初始化。"""
    app = typer.Typer()
    app.command()(main)
    project_path = tmp_path / "no-git-cli"
    result = runner.invoke(app, [str(project_path), "--no-git"], input="\n\n\n")
    assert result.exit_code == 0
    assert project_path.is_dir()
    assert not (project_path / ".git").exists()


def test_cli_force_flag(tmp_path: Path) -> None:
    """--force 应覆盖已存在目录。"""
    app = typer.Typer()
    app.command()(main)
    project_path = tmp_path / "force-cli"
    project_path.mkdir()
    (project_path / "old.txt").write_text("old")
    result = runner.invoke(app, [str(project_path), "--force"], input="\n\n\n")
    assert result.exit_code == 0
    assert not (project_path / "old.txt").exists()
    assert (project_path / "pyproject.toml").exists()


def test_cli_interactive_prompts(tmp_path: Path) -> None:
    """交互模式下应提示并注入项目描述到 README。"""
    app = typer.Typer()
    app.command()(main)
    project_path = tmp_path / "interactive-cli"
    result = runner.invoke(
        app,
        [str(project_path)],
        input="A test project\nAlice\nalice@example.com\n",
    )
    assert result.exit_code == 0
    readme = project_path / "README.md"
    assert readme.exists()
    assert "A test project" in readme.read_text(encoding="utf-8")


def test_cli_yes_skips_prompts(tmp_path: Path) -> None:
    """--yes 应跳过所有交互提示。"""
    app = typer.Typer()
    app.command()(main)
    project_path = tmp_path / "yes-cli"
    result = runner.invoke(app, [str(project_path), "--yes"])
    assert result.exit_code == 0
    readme = project_path / "README.md"
    assert readme.exists()
    content = readme.read_text(encoding="utf-8")
    assert "{project_description}" not in content


def test_generated_project_passes_make_verify(tmp_path: Path) -> None:
    """生成的项目必须能通过 make verify（lint + tests）。"""
    import subprocess
    import sys

    from harness_init.core import init_project

    project_path = tmp_path / "verify-project"
    init_project(str(project_path), no_git=True)

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", f"{project_path}[dev]"],
        check=True,
        capture_output=True,
    )

    try:
        result = subprocess.run(
            ["make", "verify"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + "\n" + result.stderr
    finally:
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", "verify_project"],
            check=False,
            capture_output=True,
        )


def test_cli_quick_flag_creates_minimal_project(tmp_path: Path) -> None:
    """--quick 应创建最小化项目，排除非必要文件。"""
    app = typer.Typer()
    app.command()(main)
    project_path = tmp_path / "quick-cli"
    result = runner.invoke(app, [str(project_path), "--quick", "--yes"])
    assert result.exit_code == 0

    # 排除的文件不应存在
    excluded_files = [
        project_path / "CLAUDE.md",
        project_path / ".cursorrules",
        project_path / ".github",
        project_path / ".pre-commit-config.yaml",
        project_path / "docs" / "decisions",
        project_path / "scripts",
    ]
    for path in excluded_files:
        assert not path.exists(), f"{path} should not exist in quick mode"

    # 必要的文件必须存在
    required_files = [
        project_path / "AGENTS.md",
        project_path / "src",
        project_path / "tests",
        project_path / "Makefile",
        project_path / "pyproject.toml",
        project_path / "README.md",
    ]
    for path in required_files:
        assert path.exists(), f"{path} must exist in quick mode"

    # AGENTS.md 应精简（≤50行）
    agents_md = project_path / "AGENTS.md"
    lines = agents_md.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 50, f"AGENTS.md has {len(lines)} lines, expected ≤50"


def test_cli_quick_and_yes_combine(tmp_path: Path) -> None:
    """--quick --yes 应无提示并创建最小化项目。"""
    app = typer.Typer()
    app.command()(main)
    project_path = tmp_path / "quick-yes-cli"
    result = runner.invoke(app, [str(project_path), "--quick", "--yes"])
    assert result.exit_code == 0

    # 不应有交互提示输出（确认使用了默认值）
    assert "Project description" not in result.output
    assert "Author name" not in result.output
    assert "Author email" not in result.output

    # 项目结构应与 --quick 单独使用相同
    excluded_files = [
        project_path / "CLAUDE.md",
        project_path / ".cursorrules",
        project_path / ".github",
    ]
    for path in excluded_files:
        assert not path.exists()

    required_files = [
        project_path / "AGENTS.md",
        project_path / "src",
        project_path / "tests",
    ]
    for path in required_files:
        assert path.exists()


def test_cli_quick_no_git(tmp_path: Path) -> None:
    """--quick --no-git 应跳过 Git 初始化。"""
    app = typer.Typer()
    app.command()(main)
    project_path = tmp_path / "quick-no-git-cli"
    result = runner.invoke(app, [str(project_path), "--quick", "--no-git", "--yes"])
    assert result.exit_code == 0

    # .git 目录不应存在
    assert not (project_path / ".git").exists()

    # 其他文件仍应正确创建
    assert (project_path / "AGENTS.md").exists()
    assert (project_path / "src").exists()
    assert (project_path / "pyproject.toml").exists()


def test_cli_quick_force(tmp_path: Path) -> None:
    """--quick --force 应覆盖已存在的目录。"""
    app = typer.Typer()
    app.command()(main)
    project_path = tmp_path / "quick-force-cli"

    # 先创建目录并添加旧文件
    project_path.mkdir()
    (project_path / "old.txt").write_text("old content")

    # 无 --force 应失败
    result = runner.invoke(app, [str(project_path), "--quick", "--yes"])
    assert result.exit_code != 0

    # 使用 --force 应成功
    result = runner.invoke(app, [str(project_path), "--quick", "--force", "--yes"])
    assert result.exit_code == 0

    # 旧文件应被覆盖
    assert not (project_path / "old.txt").exists()

    # 新文件应存在
    assert (project_path / "pyproject.toml").exists()
    assert (project_path / "AGENTS.md").exists()
