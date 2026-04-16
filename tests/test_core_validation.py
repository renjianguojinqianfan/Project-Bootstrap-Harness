"""Tests for core.py validation and force logic."""

from pathlib import Path

import pytest

from harness_init.core import init_project


def test_init_project_rejects_empty_name(tmp_path: Path) -> None:
    """应拒绝空字符串项目名。"""
    with pytest.raises(ValueError, match="cannot be empty"):
        init_project("")


def test_init_project_rejects_path_traversal(tmp_path: Path) -> None:
    """应拒绝包含路径分隔符的项目名。"""
    with pytest.raises(ValueError, match="cannot contain"):
        init_project("foo/../bar")


def test_init_project_rejects_space_in_name(tmp_path: Path) -> None:
    """应拒绝包含空格的项目名。"""
    with pytest.raises(ValueError, match="must start with a letter"):
        init_project("my project")


def test_init_project_rejects_leading_digit(tmp_path: Path) -> None:
    """应拒绝以数字开头的项目名。"""
    with pytest.raises(ValueError, match="must start with a letter"):
        init_project("123project")


def test_init_project_fails_on_existing_non_empty_dir(tmp_path: Path) -> None:
    """非空目录已存在且未指定 force 时应报错。"""
    project_path = tmp_path / "existing"
    project_path.mkdir()
    (project_path / "file.txt").write_text("hello")
    with pytest.raises(FileExistsError):
        init_project(str(project_path))


def test_init_project_rejects_existing_file(tmp_path: Path) -> None:
    """当 project_path 指向已存在的文件时应抛出 FileExistsError。"""
    file_path = tmp_path / "existing-file"
    file_path.write_text("hello")
    with pytest.raises(FileExistsError):
        init_project(str(file_path))


def test_init_project_force_backs_up_existing_dir(tmp_path: Path) -> None:
    """指定 force 时应备份已存在目录而非直接删除。"""
    project_path = tmp_path / "existing"
    project_path.mkdir()
    (project_path / "old.txt").write_text("old")
    init_project(str(project_path), force=True)
    assert not (project_path / "old.txt").exists()
    assert (project_path / "pyproject.toml").exists()
    backups = [p for p in tmp_path.iterdir() if p.name.startswith("existing.bak-")]
    assert len(backups) == 1
    assert (backups[0] / "old.txt").exists()


def test_init_project_force_uses_microsecond_backup_suffix(tmp_path: Path) -> None:
    """force 模式备份后缀应包含微秒以避免冲突。"""
    project_path = tmp_path / "backup-project"
    project_path.mkdir()
    (project_path / "file.txt").write_text("data")
    init_project(str(project_path), force=True)
    backups = [p for p in tmp_path.iterdir() if p.name.startswith("backup-project.bak-")]
    assert len(backups) == 1
    assert len(backups[0].name.split(".bak-")[-1]) == 20  # YYYYMMDDhhmmssffffff
    assert (backups[0] / "file.txt").exists()
