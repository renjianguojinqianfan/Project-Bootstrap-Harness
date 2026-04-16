"""Tests for core.py basic initialization and content."""

import sys
from pathlib import Path

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
    assert (project_path / "docs" / "decisions").is_dir()
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
    assert 'name = "test-project"' in pyproject.read_text(encoding="utf-8")


def test_init_project_creates_readme(tmp_path: Path) -> None:
    """应生成 README.md 并包含项目名。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    readme = project_path / "README.md"
    assert readme.exists()
    assert "test-project" in readme.read_text(encoding="utf-8")


def test_init_project_creates_readme_en(tmp_path: Path) -> None:
    """应生成 README.en.md 并包含项目名。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    readme = project_path / "README.en.md"
    assert readme.exists()
    assert "test-project" in readme.read_text(encoding="utf-8")


def test_init_project_creates_progress_json(tmp_path: Path) -> None:
    """应生成 .harness/progress.json。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    progress = project_path / ".harness" / "progress.json"
    assert progress.exists()
    assert '"current_plan": null' in progress.read_text(encoding="utf-8")


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


def test_init_project_creates_all_harness_and_agent_files(tmp_path: Path) -> None:
    """应生成所有 harness 和 agents 文件。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    pkg = project_path / "src" / "test_project"
    assert (pkg / "harness" / "evaluator.py").exists()
    assert (pkg / "harness" / "state.py").exists()
    assert (pkg / "harness" / "workflow.py").exists()
    assert (pkg / "agents" / "planner.py").exists()
    assert (pkg / "agents" / "generator.py").exists()
    assert (pkg / "agents" / "evaluator.py").exists()


def test_init_project_entry_point_importable(tmp_path: Path) -> None:
    """生成的 cli.py 必须能导入 cli 入口函数。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    cli_path = project_path / "src" / "test_project" / "cli.py"
    assert "def cli() -> None:" in cli_path.read_text(encoding="utf-8")


def test_init_project_pyproject_has_pythonpath(tmp_path: Path) -> None:
    """生成的 pyproject.toml 应包含 pythonpath 配置。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    pyproject = project_path / "pyproject.toml"
    assert 'pythonpath = ["src"]' in pyproject.read_text(encoding="utf-8")


def test_init_project_generated_cli_uses_typer_typer(tmp_path: Path) -> None:
    """生成的 cli.py 应使用 typer.Typer() 模式。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    content = (project_path / "src" / "test_project" / "cli.py").read_text(encoding="utf-8")
    assert "app = typer.Typer()" in content
    assert "typer.run(hello)" not in content


def test_init_project_runner_uses_posix_shlex(tmp_path: Path) -> None:
    """生成的 runner.py 应使用 posix-aware shlex.split。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    runner_path = project_path / "src" / "test_project" / "harness" / "runner.py"
    content = runner_path.read_text(encoding="utf-8")
    assert 'shlex.split(command, posix=os.name != "nt")' in content


def test_init_project_state_manager_handles_corrupt_json(tmp_path: Path) -> None:
    """StateManager 应能处理损坏的 JSON 状态文件。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    state_file = project_path / ".harness" / "state" / "state.json"
    state_file.write_text("not json", encoding="utf-8")

    pkg_src = str(project_path / "src")
    if pkg_src not in sys.path:
        sys.path.insert(0, pkg_src)
    mod = __import__("test_project.harness.state", fromlist=["StateManager"])
    sm = mod.StateManager(str(state_file))
    assert sm._data == {}


def test_init_project_gitignore_has_plans_and_eval_feedback(tmp_path: Path) -> None:
    """.gitignore 应排除 .harness/plans/ 和 .harness/eval_feedback/。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    gitignore = project_path / ".gitignore"
    content = gitignore.read_text(encoding="utf-8")
    assert ".harness/plans/" in content
    assert ".harness/eval_feedback/" in content


def test_init_project_skips_cache_files(tmp_path: Path) -> None:
    """不应把缓存文件复制到生成项目中。"""
    project_path = tmp_path / "clean-project"
    init_project(str(project_path))
    for bad in [".DS_Store", "__pycache__", "foo.pyc"]:
        assert not any(f.name == bad for f in project_path.rglob("*"))


def test_init_project_injects_metadata(tmp_path: Path) -> None:
    """应正确将描述、作者和邮箱注入到生成项目的文件和 Git 配置中。"""
    project_path = tmp_path / "meta-project"
    init_project(
        str(project_path),
        description="A meta project",
        author="Bob",
        email="bob@test.com",
    )
    readme = project_path / "README.md"
    assert "A meta project" in readme.read_text(encoding="utf-8")
    agents_md = project_path / "AGENTS.md"
    assert "A meta project" in agents_md.read_text(encoding="utf-8")
    assert "Bob" in agents_md.read_text(encoding="utf-8")
    pyproject = project_path / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    assert 'name = "Bob"' in content
    assert 'email = "bob@test.com"' in content
    git_config = (project_path / ".git" / "config").read_text(encoding="utf-8")
    assert "bob@test.com" in git_config
    assert "Bob" in git_config
