"""CLI entry point for the generated project."""

import typer

app = typer.Typer()


@app.command()
def hello(name: str = typer.Argument("World")) -> None:
    """Print a greeting message."""
    typer.echo(f"Hello, {name}!")


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo("{package_name} 0.1.0")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        is_eager=True,
        callback=version_callback,
    ),
) -> None:
    """{project_name} CLI."""


def cli() -> None:
    """Entry point for setuptools console script."""
    app()


if __name__ == "__main__":
    cli()
