"""Entry point for the surfaid_namescan CLI."""

from pathlib import Path

import click
from rich.console import Console

from validate import validate_file, add_rationale


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
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(exists=False),
    help="Output path. Will be created if it does not exist.",
)
@click.option(
    "--key",
    "-k",
    required=True,
    type=click.STRING,
    help="The namescan API key https://api.namescan.io/doc/index.html",
)
def check(file: str, output: str, key: str):
    """Validate an Excel sheet with persons against the Namescan emerald API."""
    console = create_console_logger()
    validate_file(console, Path(file), Path(output), key)


@click.command()
@click.option(
    "--file",
    "-f",
    required=True,
    type=click.Path(exists=True),
    help="Path to .xls file",
)
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(exists=False),
    help="Output path. Will be created if it does not exist.",
)
def rationale(file: str, output: str):
    """Process the output of the check command and generate a rationale for each match"""
    console = create_console_logger()
    add_rationale(console, Path(file), Path(output))


@click.group(name="namescan")
def main_group():
    """Command Line Interface for MPyL"""


if __name__ == "__main__":
    main_group.help = (
        "Validate an Excel sheet with persons against the Namescan emerald API"
    )
    main_group.add_command(check)
    main_group.add_command(rationale)
    main_group()  # pylint: disable = no-value-for-parameter
