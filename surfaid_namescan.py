from pathlib import Path

import click
from rich.console import Console

from validate import validate_file


def create_console_logger() -> Console:
    return Console(
        markup=True,
        no_color=False,
        log_path=False,
        log_time=False,
        color_system="256",
    )


@click.command()
@click.option(
    "--file",
    "-f",
    required=True,
    type=click.Path(exists=True),
    help="Path to .xls file",
)
def check(file: str):
    """Validate an Excel sheet with persons against the Namescan emerald API."""
    console = create_console_logger()
    validate_file(console, Path(file))


if __name__ == '__main__':
    check()
