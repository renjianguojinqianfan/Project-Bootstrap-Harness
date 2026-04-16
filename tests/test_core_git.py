"""Tests for core.py Git initialization logic."""

from pathlib import Path
from unittest.mock import patch

import pytest
import subprocess as sp

from harness_init.core import init_project


def test_init_project_git_identity(tmp_path: Path) -> None:
    """应在本地 Git 配置中设置 user.name 和 user.email。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    git_config = (project_path / ".git" / "config").read_text(encoding="utf-8")
    assert "harness-init@example.com" in git_config
    assert "harness-init" in git_config


def test_init_project_initializes_git(tmp_path: Path) -> None:
    """应初始化 Git 仓库并创建初始提交。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / ".git").is_dir()


def test_init_project_no_git_skips_git(tmp_path: Path) -> None:
    """指定 no_git=True 时不应创建 .git 目录。"""
    project_path = tmp_path / "no-git-project"
    init_project(str(project_path), no_git=True)
    assert project_path.is_dir()
    assert not (project_path / ".git").exists()


def test_init_project_git_failure_rolls_back(tmp_path: Path) -> None:
    """Git 初始化失败时应仅移除 .git 目录，保留项目文件。"""
    project_path = tmp_path / "rollback-project"
    with (
        patch(
            "harness_init._git.subprocess.run",
            side_effect=FileNotFoundError("git not found"),
        ),
        pytest.raises(RuntimeError, match="Git initialization failed"),
    ):
        init_project(str(project_path))
    assert project_path.is_dir()
    assert not (project_path / ".git").exists()
    assert (project_path / "src" / "rollback_project" / "cli.py").exists()


def test_init_project_git_failure_surfaces_stderr(tmp_path: Path) -> None:
    """Git 失败时应将 stderr 包含在异常信息中。"""
    project_path = tmp_path / "git-stderr-project"
    with (
        patch(
            "harness_init._git.subprocess.run",
            return_value=sp.CompletedProcess(
                args=["git", "commit", "-m", "x"],
                returncode=1,
                stdout="",
                stderr="author identity unknown",
            ),
        ),
        pytest.raises(RuntimeError, match="author identity unknown"),
    ):
        init_project(str(project_path))


def test_init_project_git_uses_fallback_when_empty(tmp_path: Path) -> None:
    """传空 author/email 时 Git 配置应回退到默认值。"""
    project_path = tmp_path / "fallback-project"
    init_project(str(project_path), description="", author="", email="")
    git_config = (project_path / ".git" / "config").read_text(encoding="utf-8")
    assert "harness-init@example.com" in git_config
    assert "harness-init" in git_config
