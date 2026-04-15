"""Tests for core.py."""

from pathlib import Path
from unittest.mock import patch

import pytest

from harness_init.core import init_project


def test_init_project_creates_directory(tmp_path: Path) -> None:
    """应创建项目根目录。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert project_path.is_dir()


def test_init_project_creates_subdirectories(tmp_path: Path) -> None:
    """应创建标准子目录结构。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / ".harness" / "plans").is_dir()
    assert (project_path / ".harness" / "eval_feedback").is_dir()
    assert (project_path / ".harness" / "state").is_dir()
    assert (project_path / ".harness" / "templates").is_dir()
    assert (project_path / ".harness" / "logs").is_dir()
    assert (project_path / "configs").is_dir()
    assert (project_path / "docs").is_dir()
    assert (project_path / "src" / "test_project").is_dir()
    assert (project_path / "src" / "test_project" / "harness").is_dir()
    assert (project_path / "src" / "test_project" / "agents").is_dir()
    assert (project_path / "src" / "test_project" / "tools").is_dir()
    assert (project_path / "src" / "test_project" / "utils").is_dir()
    assert (project_path / "tests").is_dir()


def test_init_project_creates_agents_md(tmp_path: Path) -> None:
    """AGENTS.md 应包含项目名。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    agents_md = project_path / "AGENTS.md"
    assert agents_md.exists()
    assert "test-project" in agents_md.read_text(encoding="utf-8")


def test_init_project_creates_makefile(tmp_path: Path) -> None:
    """应生成 Makefile。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / "Makefile").exists()


def test_init_project_creates_gitignore(tmp_path: Path) -> None:
    """应生成 .gitignore。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / ".gitignore").exists()


def test_init_project_creates_opencode_yaml(tmp_path: Path) -> None:
    """应生成 opencode.yaml。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / "opencode.yaml").exists()


def test_init_project_creates_pyproject_toml(tmp_path: Path) -> None:
    """应生成 pyproject.toml 并包含项目名。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    pyproject = project_path / "pyproject.toml"
    assert pyproject.exists()
    content = pyproject.read_text(encoding="utf-8")
    assert 'name = "test-project"' in content


def test_init_project_creates_readme(tmp_path: Path) -> None:
    """应生成 README.md 并包含项目名。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    readme = project_path / "README.md"
    assert readme.exists()
    assert "test-project" in readme.read_text(encoding="utf-8")


def test_init_project_creates_source_files(tmp_path: Path) -> None:
    """应生成初始源码和测试文件。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / "src" / "test_project" / "__init__.py").exists()
    assert (project_path / "src" / "test_project" / "cli.py").exists()
    assert (project_path / "src" / "test_project" / "harness" / "__init__.py").exists()
    assert (project_path / "src" / "test_project" / "agents" / "__init__.py").exists()
    assert (project_path / "src" / "test_project" / "tools" / "__init__.py").exists()
    assert (project_path / "src" / "test_project" / "utils" / "__init__.py").exists()
    assert (project_path / "tests" / "__init__.py").exists()
    assert (project_path / "tests" / "test_cli.py").exists()
    assert (project_path / "tests" / "test_harness.py").exists()


def test_init_project_generated_cli_uses_typer_typer(tmp_path: Path) -> None:
    """生成的 cli.py 应使用 typer.Typer() 模式。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    content = (project_path / "src" / "test_project" / "cli.py").read_text(encoding="utf-8")
    assert "app = typer.Typer()" in content
    assert "typer.run(hello)" not in content


def test_init_project_creates_harness_runner(tmp_path: Path) -> None:
    """应生成 harness/runner.py。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / "src" / "test_project" / "harness" / "runner.py").exists()


def test_init_project_creates_docs_context(tmp_path: Path) -> None:
    """应生成 docs/context.md。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / "docs" / "context.md").exists()


def test_init_project_creates_configs(tmp_path: Path) -> None:
    """应生成 configs/ 下的配置文件。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / "configs" / "dev.yaml").exists()
    assert (project_path / "configs" / "test.yaml").exists()
    assert (project_path / "configs" / "prod.yaml").exists()


def test_init_project_git_identity(tmp_path: Path) -> None:
    """应在本地 Git 配置中设置 user.name 和 user.email。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    git_config = (project_path / ".git" / "config").read_text(encoding="utf-8")
    assert "harness-init@localhost" in git_config
    assert "harness-init" in git_config


def test_init_project_initializes_git(tmp_path: Path) -> None:
    """应初始化 Git 仓库并创建初始提交。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    git_dir = project_path / ".git"
    assert git_dir.is_dir()


def test_init_project_rejects_empty_name(tmp_path: Path) -> None:
    """应拒绝空字符串项目名。"""
    with pytest.raises(ValueError, match="cannot be empty"):
        init_project("")


def test_init_project_rejects_path_traversal(tmp_path: Path) -> None:
    """应拒绝包含路径分隔符的项目名。"""
    with pytest.raises(ValueError, match="cannot contain"):
        init_project("foo/../bar")


def test_init_project_fails_on_existing_non_empty_dir(tmp_path: Path) -> None:
    """非空目录已存在且未指定 force 时应报错。"""
    project_path = tmp_path / "existing"
    project_path.mkdir()
    (project_path / "file.txt").write_text("hello")
    with pytest.raises(FileExistsError):
        init_project(str(project_path))


def test_init_project_force_overwrites_existing_dir(tmp_path: Path) -> None:
    """指定 force 时应覆盖已存在目录。"""
    project_path = tmp_path / "existing"
    project_path.mkdir()
    (project_path / "old.txt").write_text("old")
    init_project(str(project_path), force=True)
    assert not (project_path / "old.txt").exists()
    assert (project_path / "pyproject.toml").exists()


def test_init_project_no_git_skips_git(tmp_path: Path) -> None:
    """指定 no_git=True 时不应创建 .git 目录。"""
    project_path = tmp_path / "no-git-project"
    init_project(str(project_path), no_git=True)
    assert project_path.is_dir()
    assert not (project_path / ".git").exists()


def test_init_project_git_failure_rolls_back(tmp_path: Path) -> None:
    """Git 初始化失败时应清理已创建目录。"""
    project_path = tmp_path / "rollback-project"
    with patch(
        "harness_init.core.subprocess.run",
        side_effect=FileNotFoundError("git not found"),
    ):
        with pytest.raises(RuntimeError, match="Git initialization failed"):
            init_project(str(project_path))
    assert not project_path.exists()


def test_init_project_skips_cache_files(tmp_path: Path) -> None:
    """不应把缓存文件复制到生成项目中。"""
    project_path = tmp_path / "clean-project"
    init_project(str(project_path))
    for bad in [".DS_Store", "__pycache__", "foo.pyc"]:
        assert not any(f.name == bad for f in project_path.rglob("*"))
