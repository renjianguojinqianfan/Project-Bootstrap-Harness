"""Tests for PBH v2.0 validation and doctor commands."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from harness_init.cli import app
from harness_init.core import init_project
from harness_init.validation import (
    check_doctor,
    validate_agents_md,
    validate_file_existence,
    validate_makefile,
    validate_progress_json,
    validate_project,
)

runner = CliRunner()


def _create_compliant_project(tmp_path: Path, name: str = "test-project") -> Path:
    """Helper: create a fully compliant project via init_project."""
    project_path = tmp_path / name
    init_project(str(project_path), no_git=True)
    return project_path


# ── File Existence ────────────────────────────────────────────────────────


def test_file_existence_passes_for_compliant_project(tmp_path: Path) -> None:
    """合规项目的文件存在性检查应全部通过。"""
    project = _create_compliant_project(tmp_path)
    results = validate_file_existence(project)
    assert all(r["passed"] for r in results)


def test_file_existence_detects_missing_agents_md(tmp_path: Path) -> None:
    """缺少 AGENTS.md 应被检测到。"""
    project = _create_compliant_project(tmp_path)
    (project / "AGENTS.md").unlink()
    results = validate_file_existence(project)
    failed = [r for r in results if not r["passed"]]
    assert any("AGENTS.md" in r["check"] for r in failed)


def test_file_existence_detects_missing_makefile(tmp_path: Path) -> None:
    """缺少 Makefile 应被检测到。"""
    project = _create_compliant_project(tmp_path)
    (project / "Makefile").unlink()
    results = validate_file_existence(project)
    failed = [r for r in results if not r["passed"]]
    assert any("Makefile" in r["check"] for r in failed)


def test_file_existence_detects_missing_progress_json(tmp_path: Path) -> None:
    """缺少 .harness/progress.json 应被检测到。"""
    project = _create_compliant_project(tmp_path)
    (project / ".harness" / "progress.json").unlink()
    results = validate_file_existence(project)
    failed = [r for r in results if not r["passed"]]
    assert any("progress.json" in r["check"] for r in failed)


# ── AGENTS.md Content ────────────────────────────────────────────────────


def test_agents_md_passes_for_compliant_project(tmp_path: Path) -> None:
    """合规项目的 AGENTS.md 内容检查应全部通过。"""
    project = _create_compliant_project(tmp_path)
    results = validate_agents_md(project)
    assert all(r["passed"] for r in results)


def test_agents_md_detects_missing_snapshot(tmp_path: Path) -> None:
    """缺少 §Project Snapshot 应被检测到。"""
    project = _create_compliant_project(tmp_path)
    agents = project / "AGENTS.md"
    content = agents.read_text(encoding="utf-8")
    content = content.replace("## 1. Project Snapshot", "## 1. Removed Section")
    agents.write_text(content, encoding="utf-8")
    results = validate_agents_md(project)
    failed = [r for r in results if not r["passed"]]
    assert any("snapshot" in r["check"].lower() for r in failed)


def test_agents_md_detects_missing_quick_start(tmp_path: Path) -> None:
    """缺少 §Quick Start 应被检测到。"""
    project = _create_compliant_project(tmp_path)
    agents = project / "AGENTS.md"
    content = agents.read_text(encoding="utf-8")
    content = content.replace("## 2. Quick Start", "## 2. Removed")
    agents.write_text(content, encoding="utf-8")
    results = validate_agents_md(project)
    failed = [r for r in results if not r["passed"]]
    assert any("quick_start" in r["check"].lower() for r in failed)


def test_agents_md_detects_missing_critical_rules(tmp_path: Path) -> None:
    """缺少 §Critical Rules 应被检测到。"""
    project = _create_compliant_project(tmp_path)
    agents = project / "AGENTS.md"
    content = agents.read_text(encoding="utf-8")
    content = content.replace("## 5. Critical Rules", "## 5. Removed")
    agents.write_text(content, encoding="utf-8")
    results = validate_agents_md(project)
    failed = [r for r in results if not r["passed"]]
    assert any("critical_rules" in r["check"].lower() for r in failed)


def test_agents_md_detects_missing_file_mapping(tmp_path: Path) -> None:
    """缺少 §File Mapping 应被检测到。"""
    project = _create_compliant_project(tmp_path)
    agents = project / "AGENTS.md"
    content = agents.read_text(encoding="utf-8")
    content = content.replace("## 8. File Mapping", "## 8. Removed")
    agents.write_text(content, encoding="utf-8")
    results = validate_agents_md(project)
    failed = [r for r in results if not r["passed"]]
    assert any("file_mapping" in r["check"].lower() for r in failed)


def test_agents_md_detects_missing_commands(tmp_path: Path) -> None:
    """缺少 §Commands 应被检测到。"""
    project = _create_compliant_project(tmp_path)
    agents = project / "AGENTS.md"
    content = agents.read_text(encoding="utf-8")
    content = content.replace("## 9. Commands", "## 9. Removed")
    agents.write_text(content, encoding="utf-8")
    results = validate_agents_md(project)
    failed = [r for r in results if not r["passed"]]
    assert any("commands" in r["check"].lower() for r in failed)


def test_agents_md_detects_quick_start_not_make_verify_first(tmp_path: Path) -> None:
    """Quick Start 第一步不是 make verify 应被检测到。"""
    project = _create_compliant_project(tmp_path)
    agents = project / "AGENTS.md"
    content = agents.read_text(encoding="utf-8")
    content = content.replace(
        "1. Run `make verify`",
        "1. Run `echo hello`",
    )
    agents.write_text(content, encoding="utf-8")
    results = validate_agents_md(project)
    failed = [r for r in results if not r["passed"]]
    assert any("make verify" in r["check"].lower() for r in failed)


def test_agents_md_handles_read_error(tmp_path: Path) -> None:
    """AGENTS.md 不可读时应返回错误结果。"""
    project = _create_compliant_project(tmp_path)
    agents = project / "AGENTS.md"
    agents.unlink()
    agents.mkdir()  # Replace file with directory to cause read error
    results = validate_agents_md(project)
    assert any(not r["passed"] for r in results)


# ── progress.json ─────────────────────────────────────────────────────────


def test_progress_json_passes_for_compliant_project(tmp_path: Path) -> None:
    """合规项目的 progress.json 检查应全部通过。"""
    project = _create_compliant_project(tmp_path)
    results = validate_progress_json(project)
    assert all(r["passed"] for r in results)


def test_progress_json_detects_invalid_json(tmp_path: Path) -> None:
    """无效 JSON 应被检测到。"""
    project = _create_compliant_project(tmp_path)
    pj = project / ".harness" / "progress.json"
    pj.write_text("not valid json {{{", encoding="utf-8")
    results = validate_progress_json(project)
    assert any(not r["passed"] for r in results)


def test_progress_json_detects_missing_project_name(tmp_path: Path) -> None:
    """缺少 project_name 字段应被检测到。"""
    project = _create_compliant_project(tmp_path)
    pj = project / ".harness" / "progress.json"
    data = {"current_stage": "init", "plans": [], "last_updated": "2026-01-01T00:00:00"}
    pj.write_text(json.dumps(data), encoding="utf-8")
    results = validate_progress_json(project)
    failed = [r for r in results if not r["passed"]]
    assert any("project_name" in r["check"] for r in failed)


def test_progress_json_detects_invalid_stage(tmp_path: Path) -> None:
    """无效的 current_stage 值应被检测到。"""
    project = _create_compliant_project(tmp_path)
    pj = project / ".harness" / "progress.json"
    data = {
        "project_name": "test",
        "current_stage": "invalid_stage",
        "plans": [],
        "last_updated": "2026-01-01T00:00:00",
    }
    pj.write_text(json.dumps(data), encoding="utf-8")
    results = validate_progress_json(project)
    failed = [r for r in results if not r["passed"]]
    assert any("current_stage" in r["check"] for r in failed)


def test_progress_json_detects_missing_plans(tmp_path: Path) -> None:
    """缺少 plans 字段应被检测到。"""
    project = _create_compliant_project(tmp_path)
    pj = project / ".harness" / "progress.json"
    data = {
        "project_name": "test",
        "current_stage": "init",
        "last_updated": "2026-01-01T00:00:00",
    }
    pj.write_text(json.dumps(data), encoding="utf-8")
    results = validate_progress_json(project)
    failed = [r for r in results if not r["passed"]]
    assert any("plans" in r["check"] for r in failed)


def test_progress_json_detects_invalid_last_updated(tmp_path: Path) -> None:
    """非 ISO 8601 格式的 last_updated 应被检测到。"""
    project = _create_compliant_project(tmp_path)
    pj = project / ".harness" / "progress.json"
    data = {
        "project_name": "test",
        "current_stage": "init",
        "plans": [],
        "last_updated": "not-a-date",
    }
    pj.write_text(json.dumps(data), encoding="utf-8")
    results = validate_progress_json(project)
    failed = [r for r in results if not r["passed"]]
    assert any("last_updated" in r["check"] for r in failed)


def test_progress_json_accepts_all_valid_stages(tmp_path: Path) -> None:
    """所有合法的 current_stage 值都应被接受。"""
    for stage in ("init", "plan", "execute", "evaluate", "done"):
        project = _create_compliant_project(tmp_path, f"stage-{stage}")
        pj = project / ".harness" / "progress.json"
        data = {
            "project_name": f"stage-{stage}",
            "current_stage": stage,
            "plans": [],
            "last_updated": "2026-01-01T00:00:00",
        }
        pj.write_text(json.dumps(data), encoding="utf-8")
        results = validate_progress_json(project)
        stage_result = next(r for r in results if "current_stage" in r["check"])
        assert stage_result["passed"], f"Stage '{stage}' should be valid"


# ── Makefile ──────────────────────────────────────────────────────────────


def test_makefile_passes_for_compliant_project(tmp_path: Path) -> None:
    """合规项目的 Makefile 检查应通过。"""
    project = _create_compliant_project(tmp_path)
    results = validate_makefile(project)
    assert all(r["passed"] for r in results)


def test_makefile_detects_missing_verify_target(tmp_path: Path) -> None:
    """Makefile 缺少 verify target 应被检测到。"""
    project = _create_compliant_project(tmp_path)
    makefile = project / "Makefile"
    makefile.write_text("test:\n\tpytest\n", encoding="utf-8")
    results = validate_makefile(project)
    assert any(not r["passed"] for r in results)


# ── Full validate_project ─────────────────────────────────────────────────


def test_validate_project_passes_for_compliant_project(tmp_path: Path) -> None:
    """完整合规项目应通过所有验证。"""
    project = _create_compliant_project(tmp_path)
    # Skip make verify in tests (requires installed dependencies)
    all_passed, results = validate_project(str(project))
    # Filter out make verify (behavioral) since we can't run it in unit tests
    non_behavioral = [r for r in results if r["check"] != "make verify passes"]
    assert all(r["passed"] for r in non_behavioral)


def test_validate_project_fails_for_empty_dir(tmp_path: Path) -> None:
    """空目录应无法通过验证。"""
    empty = tmp_path / "empty"
    empty.mkdir()
    all_passed, results = validate_project(str(empty))
    assert not all_passed


# ── Doctor ────────────────────────────────────────────────────────────────


def test_doctor_checks_make() -> None:
    """doctor 应检查 make 命令。"""
    _, results = check_doctor()
    checks = [r["check"] for r in results]
    assert any("make" in c for c in checks)


def test_doctor_checks_git() -> None:
    """doctor 应检查 git 命令。"""
    _, results = check_doctor()
    checks = [r["check"] for r in results]
    assert any("git" in c for c in checks)


def test_doctor_checks_python() -> None:
    """doctor 应检查 python 命令。"""
    _, results = check_doctor()
    checks = [r["check"] for r in results]
    assert any("python" in c for c in checks)


def test_doctor_checks_python_version() -> None:
    """doctor 应检查 Python 版本。"""
    _, results = check_doctor()
    version_check = next(r for r in results if "3.11" in r["check"])
    assert version_check["passed"]


def test_doctor_reports_missing_tool() -> None:
    """当工具缺失时 doctor 应报告失败。"""
    with patch("shutil.which", return_value=None):
        all_ok, results = check_doctor()
        assert not all_ok
        assert any(not r["passed"] for r in results)


# ── CLI Commands ──────────────────────────────────────────────────────────


def test_cli_validate_compliant_project(tmp_path: Path) -> None:
    """CLI validate 命令应对合规项目输出成功。"""
    project = _create_compliant_project(tmp_path)
    result = runner.invoke(app, ["validate", str(project)])
    # Should output compliance check results
    assert "PBH v2.0 Compliance Check" in result.output


def test_cli_validate_nonexistent_path(tmp_path: Path) -> None:
    """CLI validate 命令应对不存在的路径输出失败。"""
    result = runner.invoke(app, ["validate", str(tmp_path / "nonexistent")])
    assert result.exit_code != 0


def test_cli_doctor_outputs_results() -> None:
    """CLI doctor 命令应输出环境检查结果。"""
    result = runner.invoke(app, ["doctor"])
    assert "Environment Check" in result.output


def test_cli_validate_default_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI validate 命令不带参数时应使用当前目录。"""
    project = _create_compliant_project(tmp_path)
    monkeypatch.chdir(project)
    result = runner.invoke(app, ["validate"])
    assert "PBH v2.0 Compliance Check" in result.output
