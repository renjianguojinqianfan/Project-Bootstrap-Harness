"""CLI entry for harness-init."""

import typer

from harness_init import __version__
from harness_init.core import init_project
from harness_init.validation import check_doctor, validate_project

app = typer.Typer(help="PBH v2.0 项目脚手架与合规性验证工具。")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"harness-init {__version__}")
        raise typer.Exit()


@app.callback()
def _global_options(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        is_eager=True,
        callback=_version_callback,
    ),
) -> None:
    """PBH v2.0 项目脚手架与合规性验证工具。"""


def _run_init(
    project_name: str,
    force: bool = False,
    no_git: bool = False,
    description: str = "",
    author: str = "",
    email: str = "",
    quick: bool = False,
    template: str = "cli",
    ide: str = "all",
) -> None:
    """纯 Python 入口，供 CLI 和测试直接调用。"""
    kwargs = {
        "description": description,
        "author": author,
        "email": email,
        "template": template,
        "ide": ide,
    }
    if force:
        kwargs["force"] = True
    if no_git:
        kwargs["no_git"] = True
    if quick:
        kwargs["quick"] = True
    init_project(project_name, **kwargs)


def _prompt_metadata(yes: bool) -> tuple[str, str, str]:
    """Prompt for project metadata unless --yes is set."""
    if yes:
        return "", "", ""
    description = typer.prompt("Project description", default="")
    author = typer.prompt("Author name", default="")
    email = typer.prompt("Author email", default="")
    return description, author, email


@app.command()
def init(
    project_name: str = typer.Argument(..., help="项目名称或目标路径。"),
    force: bool = typer.Option(False, "--force", "-f", help="强制覆盖已存在目录。"),
    no_git: bool = typer.Option(False, "--no-git", help="跳过 Git 初始化。"),
    yes: bool = typer.Option(False, "--yes", "-y", help="跳过交互提示，使用默认值。"),
    quick: bool = typer.Option(False, "--quick", "-q", help="生成精简项目。"),
    template: str = typer.Option(
        "cli", "--template", "-t", help="项目模板类型（cli/lib/web/notebook）。"
    ),
    ide: str = typer.Option(
        "all", "--ide", help="IDE 配置模式（all/none/cursor/claude/trae/copilot/opencode）。"
    ),
) -> None:
    """初始化一个新的 Harness Engineering 项目。"""
    description, author, email = _prompt_metadata(yes)
    _run_init(
        project_name,
        force=force,
        no_git=no_git,
        description=description,
        author=author,
        email=email,
        quick=quick,
        template=template,
        ide=ide,
    )


def _print_results(title: str, results: list[dict]) -> None:
    """Pretty-print a list of validation results."""
    typer.echo(f"\n{'=' * 50}")
    typer.echo(f"  {title}")
    typer.echo(f"{'=' * 50}")
    for r in results:
        icon = "✅" if r["passed"] else "❌"
        typer.echo(f"  {icon} {r['check']}: {r['message']}")


@app.command()
def validate(
    project_path: str = typer.Argument(".", help="要验证的项目路径。默认为当前目录。"),
) -> None:
    """检查项目是否符合 PBH v2.0 协议规范。

    验证内容包括：文件存在性、内容合规性、行为合规性（make verify）。
    """
    all_passed, results = validate_project(project_path)

    _print_results("PBH v2.0 Compliance Check", results)

    typer.echo(f"\n{'=' * 50}")
    if all_passed:
        typer.echo("  🎉 项目符合 PBH v2.0 协议规范！")
    else:
        typer.echo("  ⚠️  项目未通过合规性检查，请修复上述问题。")
        raise typer.Exit(code=1)


@app.command()
def doctor() -> None:
    """检查本地开发环境是否满足 PBH 协作前提条件。

    检查 make、git、python、pip 等工具是否可用。
    """
    all_ok, results = check_doctor()

    _print_results("Environment Check", results)

    typer.echo(f"\n{'=' * 50}")
    if all_ok:
        typer.echo("  🎉 开发环境满足协议协作条件！")
    else:
        typer.echo("  ⚠️  环境不满足条件，请安装缺失的工具。")
        raise typer.Exit(code=1)


def main(
    project_name: str = typer.Argument(..., help="项目名称或目标路径。"),
    force: bool = typer.Option(False, "--force", "-f", help="强制覆盖已存在目录。"),
    no_git: bool = typer.Option(False, "--no-git", help="跳过 Git 初始化。"),
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit。", is_eager=True, callback=_version_callback
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="跳过交互提示，使用默认值。"),
    quick: bool = typer.Option(False, "--quick", "-q", help="生成精简项目。"),
    template: str = typer.Option(
        "cli", "--template", "-t", help="项目模板类型（cli/lib/web/notebook）。"
    ),
    ide: str = typer.Option(
        "all", "--ide", help="IDE 配置模式（all/none/cursor/claude/trae/copilot/opencode）。"
    ),
) -> None:
    """初始化一个新的 Harness Engineering 项目。"""
    description, author, email = _prompt_metadata(yes)
    _run_init(
        project_name,
        force=force,
        no_git=no_git,
        description=description,
        author=author,
        email=email,
        quick=quick,
        template=template,
        ide=ide,
    )


def cli() -> None:
    """CLI entry point."""
    app()


if __name__ == "__main__":
    cli()
