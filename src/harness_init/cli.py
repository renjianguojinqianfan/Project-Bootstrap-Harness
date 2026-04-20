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
    quick: bool = False,
) -> None:
    """纯 Python 入口，供 CLI 和测试直接调用。"""
    kwargs = {}
    if force:
        kwargs["force"] = True
    if no_git:
        kwargs["no_git"] = True
    if quick:
        kwargs["quick"] = True
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
    yes: bool = typer.Option(False, "--yes", "-y", help="跳过交互提示，使用默认值。"),
    quick: bool = typer.Option(False, "--quick", "-q", help="生成精简项目（无 CI/文档/钩子/IDE 配置）。"),
) -> None:
    """初始化一个新的 Harness Engineering 项目。"""
    description = "" if yes else typer.prompt("Project description", default="")
    author = "" if yes else typer.prompt("Author name", default="")
    email = "" if yes else typer.prompt("Author email", default="")
    _run_init(
        project_name,
        force=force,
        no_git=no_git,
        description=description,
        author=author,
        email=email,
        quick=quick,
    )


def cli() -> None:
    """CLI entry point."""
    typer.run(main)


if __name__ == "__main__":
    cli()
