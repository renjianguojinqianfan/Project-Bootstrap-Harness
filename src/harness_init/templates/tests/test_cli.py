"""Tests for cli.py."""

from typer.testing import CliRunner

from {package_name}.cli import app

runner = CliRunner()


def test_hello_default() -> None:
    """hello should print greeting with default name."""
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.output


def test_hello_with_name() -> None:
    """hello should print greeting with provided name."""
    result = runner.invoke(app, ["hello", "Alice"])
    assert result.exit_code == 0
    assert "Hello, Alice!" in result.output


def test_version_flag() -> None:
    """--version should print version and exit."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_version_short_flag() -> None:
    """-v should print version and exit."""
    result = runner.invoke(app, ["-v"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
