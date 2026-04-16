"""CLI entry for harness-init."""

import typer

from harness_init import __version__
from harness_init.core import init_project


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"harness-init {__version__}")
        raise typer.Exit()


def _run_init(
    project_name: str,
    force: bool = False,
    no_git: bool = False,
    description: str = "",
    author: str = "",
    email: str = "",
) -> None:
    """纯 Python 入口，供 CLI 和测试直接调用。"""
    kwargs = {}
    if force:
        kwargs["force"] = True
    if no_git:
        kwargs["no_git"] = True
    kwargs["description"] = description
    kwargs["author"] = author
    kwargs["email"] = email
    init_project(project_name, **kwargs)


def main(
    project_name: str = typer.Argument(..., help="项目名称或目标路径。"),
    force: bool = typer.Option(False, "--force", "-f", help="强制覆盖已存在目录。"),
    no_git: bool = typer.Option(False, "--no-git", help="跳过 Git 初始化。"),
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit。",
        is_eager=True,
        callback=_version_callback,
    ),
    description: str = typer.Option("", prompt="Project description", help="项目描述。"),
    author: str = typer.Option("", prompt="Author name", help="作者名。"),
    email: str = typer.Option("", prompt="Author email", help="作者邮箱。"),
    yes: bool = typer.Option(False, "--yes", "-y", help="跳过交互提示，使用默认值。"),
) -> None:
    """初始化一个新的 Harness Engineering 项目。"""
    _run_init(
        project_name,
        force=force,
        no_git=no_git,
        description="" if yes else description,
        author="" if yes else author,
        email="" if yes else email,
    )


def cli() -> None:
    """CLI entry point."""
    typer.run(main)


if __name__ == "__main__":
    cli()
