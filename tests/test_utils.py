"""Tests for _utils.py."""

import re
from pathlib import Path

from harness_init._utils import _copy_or_render_template


def test_copy_or_render_replaces_project_type_and_date(tmp_path: Path) -> None:
    """_copy_or_render_template 应替换 {project_type} 和 {generated_date}。"""
    template = tmp_path / "template.txt"
    template.write_text("Type: {project_type}, Date: {generated_date}", encoding="utf-8")
    output = tmp_path / "output.txt"
    _copy_or_render_template(template, output, "my-project")
    content = output.read_text(encoding="utf-8")
    assert "Type: cli" in content
    assert re.search(r"Date: \d{4}-\d{2}-\d{2}", content)
    assert "{project_type}" not in content
    assert "{generated_date}" not in content
