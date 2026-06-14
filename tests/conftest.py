"""Shared pytest fixtures for the harness-init test suite."""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _change_to_tmp_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run every test inside its temporary directory.

    This lets tests use simple project names instead of absolute tmp paths,
    which keeps input validation focused on single directory names.
    """
    monkeypatch.chdir(tmp_path)
