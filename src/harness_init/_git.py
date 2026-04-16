"""Git helpers for harness-init."""

import os
import stat
import subprocess
from pathlib import Path


def _git(project_path: Path, *args: str) -> None:
    """运行 Git 命令，失败时抛出包含 stderr 的异常。"""
    result = subprocess.run(["git", *args], cwd=project_path, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")


def _init_git(project_path: Path, author: str = "", email: str = "") -> None:
    """初始化 Git 仓库并创建初始提交。"""
    _git(project_path, "init")
    _git(project_path, "config", "user.email", email or "harness-init@example.com")
    _git(project_path, "config", "user.name", author or "harness-init")
    _git(project_path, "add", ".")
    _git(project_path, "commit", "-m", "Initial commit")


def _on_remove_error(_func: object, path: str, _exc_info: object) -> None:
    """Windows 下删除只读文件时的回调。"""
    os.chmod(path, stat.S_IWRITE)
    if os.path.isdir(path) and not os.path.islink(path):
        os.rmdir(path)
    else:
        os.unlink(path)
