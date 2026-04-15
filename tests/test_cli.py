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
    result = runner.invoke(app, [str(project_path)])
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
    result = runner.invoke(app, [str(project_path), "--no-git"])
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
    result = runner.invoke(app, [str(project_path), "--force"])
    assert result.exit_code == 0
    assert not (project_path / "old.txt").exists()
    assert (project_path / "pyproject.toml").exists()
