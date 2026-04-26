"""Tests for core.py basic initialization and content."""

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
    assert (project_path / ".github" / "workflows").is_dir()
    assert (project_path / ".harness" / "templates").is_dir()
    assert (project_path / "docs").is_dir()
    assert (project_path / "src" / "test_project").is_dir()
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


def test_init_project_creates_cursorrules(tmp_path: Path) -> None:
    """应生成 .cursorrules。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    cursorrules = project_path / ".cursorrules"
    assert cursorrules.exists()
    content = cursorrules.read_text(encoding="utf-8")
    assert "test-project" in content


def test_init_project_creates_pre_commit_config(tmp_path: Path) -> None:
    """应生成 .pre-commit-config.yaml。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / ".pre-commit-config.yaml").exists()


def test_init_project_creates_ci_workflow(tmp_path: Path) -> None:
    """应生成 .github/workflows/ci.yml。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / ".github" / "workflows" / "ci.yml").exists()


def test_init_project_creates_pre_push_sh(tmp_path: Path) -> None:
    """应生成 scripts/pre-push.sh。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / "scripts" / "pre-push.sh").exists()


def test_init_project_creates_pre_push_ps1(tmp_path: Path) -> None:
    """应生成 scripts/pre-push.ps1。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / "scripts" / "pre-push.ps1").exists()


def test_init_project_creates_project_map(tmp_path: Path) -> None:
    """应生成 docs/PROJECT_MAP.md。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / "docs" / "PROJECT_MAP.md").exists()


def test_init_project_creates_adr_template(tmp_path: Path) -> None:
    """应生成 docs/decisions/ADR_TEMPLATE.md。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / "docs" / "decisions" / "ADR_TEMPLATE.md").exists()


def test_init_project_creates_claude_md(tmp_path: Path) -> None:
    """应生成 CLAUDE.md。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / "CLAUDE.md").exists()


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
    import json

    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    progress = project_path / ".harness" / "progress.json"
    assert progress.exists()
    data = json.loads(progress.read_text(encoding="utf-8"))
    assert data["project_name"] == "test-project"
    assert data["current_stage"] == "init"
    assert data["plans"] == []
    assert "last_updated" in data


def test_init_project_agents_md_has_rules(tmp_path: Path) -> None:
    """AGENTS.md 应包含致命规则。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    agents_md = project_path / "AGENTS.md"
    content = agents_md.read_text(encoding="utf-8")
    assert "make verify" in content
    assert "Critical Rules" in content


def test_init_project_creates_plan_template_json(tmp_path: Path) -> None:
    """应生成 .harness/templates/plan_template.json 且为有效 JSON。"""
    import json

    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    plan_template = project_path / ".harness" / "templates" / "plan_template.json"
    assert plan_template.exists()
    data = json.loads(plan_template.read_text(encoding="utf-8"))
    assert "goal" in data["$schema"]["properties"]
    assert "steps" in data["$schema"]["properties"]
    assert "acceptance_criteria" in data["$schema"]["properties"]
    assert "template_example" in data


def test_init_project_creates_source_files(tmp_path: Path) -> None:
    """应生成初始源码和测试文件。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / "src" / "test_project" / "__init__.py").exists()
    assert (project_path / "src" / "test_project" / "cli.py").exists()
    assert (project_path / "tests" / "__init__.py").exists()
    assert (project_path / "tests" / "test_cli.py").exists()


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


def test_init_project_creates_tasks_directory(tmp_path: Path) -> None:
    """应生成 tasks/ 目录和 task_plan.md 模板。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    assert (project_path / "tasks").is_dir()
    task_plan = project_path / "tasks" / "task_plan.md"
    assert task_plan.exists()
    content = task_plan.read_text(encoding="utf-8")
    assert "Task Plan" in content
    assert "Phase 1" in content


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


def test_init_project_gitignore_has_harness_entries(tmp_path: Path) -> None:
    """.gitignore 应排除 .harness 相关目录。"""
    project_path = tmp_path / "test-project"
    init_project(str(project_path))
    gitignore = project_path / ".gitignore"
    content = gitignore.read_text(encoding="utf-8")
    assert ".harness/logs/" in content


def test_init_project_skips_cache_files(tmp_path: Path) -> None:
    """不应把缓存文件复制到生成项目中。"""
    project_path = tmp_path / "clean-project"
    init_project(str(project_path))
    for bad in [".DS_Store", "__pycache__", "foo.pyc"]:
        assert not any(f.name == bad for f in project_path.rglob("*"))


def test_init_project_quick_creates_minimal_structure(tmp_path: Path) -> None:
    """quick=True 应创建精简的项目结构。"""
    project_path = tmp_path / "quick-proj"
    init_project(str(project_path), quick=True)
    assert (project_path / "src" / "quick_proj").is_dir()
    assert (project_path / "tests").is_dir()
    assert (project_path / ".harness").is_dir()
    assert (project_path / "AGENTS.md").exists()
    assert (project_path / "Makefile").exists()
    assert (project_path / "pyproject.toml").exists()
    assert (project_path / "README.md").exists()
    assert (project_path / ".gitignore").exists()


def test_init_project_quick_excludes_files(tmp_path: Path) -> None:
    """quick=True 应排除完整模式的文件和目录。"""
    project_path = tmp_path / "quick-proj"
    init_project(str(project_path), quick=True)
    assert not (project_path / "CLAUDE.md").exists()
    assert not (project_path / ".cursorrules").exists()
    assert not (project_path / ".github").exists()
    assert not (project_path / ".pre-commit-config.yaml").exists()
    assert not (project_path / "docs" / "decisions").exists()
    assert not (project_path / "scripts").exists()
    assert not (project_path / "configs").exists()
    assert not (project_path / "opencode.yaml").exists()
    assert not (project_path / "tests" / "test_harness.py").exists()


def test_init_project_quick_agents_md_is_short(tmp_path: Path) -> None:
    """quick=True 生成的 AGENTS.md 应不超过 50 行。"""
    project_path = tmp_path / "quick-proj"
    init_project(str(project_path), quick=True)
    agents_md = project_path / "AGENTS.md"
    assert agents_md.exists()
    lines = agents_md.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 50


def test_init_project_quick_pyproject_has_minimal_deps(tmp_path: Path) -> None:
    """quick=True 生成的 pyproject.toml 应只包含最小依赖。"""
    project_path = tmp_path / "quick-proj"
    init_project(str(project_path), quick=True)
    pyproject = project_path / "pyproject.toml"
    assert pyproject.exists()
    content = pyproject.read_text(encoding="utf-8")
    assert "pydantic" not in content
    assert "pyyaml" not in content
    assert "rich" not in content
    assert "typer" in content


def test_init_project_quick_uses_quick_templates(tmp_path: Path) -> None:
    """quick=True 应使用 quick 模板生成源码和测试文件。"""
    project_path = tmp_path / "quick-proj"
    init_project(str(project_path), quick=True)
    cli_path = project_path / "src" / "quick_proj" / "cli.py"
    test_cli_path = project_path / "tests" / "test_cli.py"
    assert cli_path.exists()
    assert test_cli_path.exists()
    cli_content = cli_path.read_text(encoding="utf-8")
    # quick 模板不应包含 harness 相关导入
    assert "harness" not in cli_content
    test_content = test_cli_path.read_text(encoding="utf-8")
    # quick 测试模板应测试 hello 命令和 version
    assert "hello" in test_content
    assert "0.1.0" in test_content


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
    project_map = project_path / "docs" / "PROJECT_MAP.md"
    assert project_map.exists()
    pm_content = project_map.read_text(encoding="utf-8")
    assert "cli" in pm_content  # project_type default
    assert "{{generated_date}}" not in pm_content
    assert "{generated_date}" not in pm_content  # should be replaced


def test_init_project_replaces_project_type(tmp_path: Path) -> None:
    """AGENTS.md 和 CLAUDE.md 应正确替换 {project_type}。"""
    project_path = tmp_path / "type-project"
    init_project(str(project_path))
    agents_md = (project_path / "AGENTS.md").read_text(encoding="utf-8")
    claude_md = (project_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "{project_type}" not in agents_md
    assert "{project_type}" not in claude_md
    assert "cli" in agents_md
    assert "cli" in claude_md


def test_generated_project_document_consistency(tmp_path: Path) -> None:
    """验证生成项目的关键文档之间的一致性。"""
    import json

    project_path = tmp_path / "consistency-project"
    init_project(str(project_path))
    agents_md = (project_path / "AGENTS.md").read_text(encoding="utf-8")
    plan_template = project_path / ".harness" / "templates" / "plan_template.json"
    assert "make verify" in agents_md
    assert "Critical Rules" in agents_md
    assert len(agents_md.splitlines()) <= 110
    plan_data = json.loads(plan_template.read_text(encoding="utf-8"))
    assert "goal" in plan_data["$schema"]["properties"]
    assert "steps" in plan_data["$schema"]["properties"]


def test_init_project_template_lib(tmp_path: Path) -> None:
    """--template=lib 应生成库项目结构。"""
    project_path = tmp_path / "lib-project"
    init_project(str(project_path), template="lib")
    assert (project_path / "src" / "lib_project" / "__init__.py").exists()
    assert not (project_path / "src" / "lib_project" / "cli.py").exists()
    pyproject = (project_path / "pyproject.toml").read_text(encoding="utf-8")
    assert "[project.scripts]" not in pyproject


def test_init_project_template_web(tmp_path: Path) -> None:
    """--template=web 应生成 FastAPI 项目结构。"""
    project_path = tmp_path / "web-project"
    init_project(str(project_path), template="web")
    assert (project_path / "src" / "web_project" / "main.py").exists()
    pyproject = (project_path / "pyproject.toml").read_text(encoding="utf-8")
    assert "fastapi" in pyproject


def test_init_project_template_notebook(tmp_path: Path) -> None:
    """--template=notebook 应生成 notebook 项目结构。"""
    project_path = tmp_path / "nb-project"
    init_project(str(project_path), template="notebook")
    assert (project_path / "notebooks" / "example.ipynb").exists()
    assert not (project_path / "src").exists()


def test_init_project_invalid_template(tmp_path: Path) -> None:
    """无效模板应引发 ValueError。"""
    with pytest.raises(ValueError, match="Unknown template"):
        init_project(str(tmp_path / "bad-project"), template="invalid")


def test_init_project_ide_cursor_only(tmp_path: Path) -> None:
    """ide=cursor 应只保留 Cursor 配置。"""
    project_path = tmp_path / "cursor-project"
    init_project(str(project_path), ide="cursor")
    assert (project_path / ".cursorrules").exists()
    assert not (project_path / "CLAUDE.md").exists()
    assert not (project_path / "opencode.yaml").exists()
    assert not (project_path / ".trae").exists()
    assert not (project_path / ".github" / "copilot-instructions.md").exists()


def test_init_project_ide_none(tmp_path: Path) -> None:
    """ide=none 应排除所有 IDE 配置。"""
    project_path = tmp_path / "none-project"
    init_project(str(project_path), ide="none")
    assert not (project_path / ".cursorrules").exists()
    assert not (project_path / "CLAUDE.md").exists()
    assert not (project_path / "opencode.yaml").exists()
    assert not (project_path / ".trae").exists()
    assert not (project_path / ".github" / "copilot-instructions.md").exists()


def test_init_project_ide_all(tmp_path: Path) -> None:
    """ide=all 应保留所有 IDE 配置。"""
    project_path = tmp_path / "all-project"
    init_project(str(project_path), ide="all")
    assert (project_path / ".cursorrules").exists()
    assert (project_path / "CLAUDE.md").exists()
    assert (project_path / "opencode.yaml").exists()
    assert (project_path / ".trae").exists()
    assert (project_path / ".github" / "copilot-instructions.md").exists()


def test_init_project_creates_known_pitfalls(tmp_path: Path) -> None:
    """应创建 .harness/known_pitfalls.md。"""
    project_path = tmp_path / "pitfalls-project"
    init_project(str(project_path))
    pitfalls = project_path / ".harness" / "known_pitfalls.md"
    assert pitfalls.exists()
    content = pitfalls.read_text(encoding="utf-8")
    assert "Known Pitfalls" in content
