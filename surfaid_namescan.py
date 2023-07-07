"""Entry point for the surfaid_namescan CLI."""
import sys
from contextlib import redirect_stderr
from pathlib import Path
from typing import Optional

print(  # pylint: disable=wrong-import-position
    "Surfaid Namescan CLI © 2023. Starting up..."
)

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


def to_output_path(input_file: Path, output: Optional[str]) -> Path:
    return (
        Path(input_file.parent, output)
        if output
        else Path(input_file.parent, input_file.stem)
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
    required=False,
    type=click.Path(exists=False),
    help="Optional output path. Same as input file name by default. Will be created if it does not exist.",
)
@click.option(
    "--key",
    "-k",
    required=True,
    type=click.STRING,
    help="The namescan API key https://api.namescan.io/doc/index.html",
)
@click.option(
    "--entity",
    "-e",
    required=False,
    type=click.Choice(["organization", "person"]),
    default="person",
    help="The type of scan to do. Default is person.",
)
def check(file: str, output: Optional[str], key: str, entity: str):
    """Validate an Excel sheet with persons against the Namescan emerald API."""
    console = create_console_logger()

    input_file = Path(file)
    output_path = to_output_path(input_file, output)

    validate_file(console, input_file, output_path, key, entity)
    add_rationale(console, input_file, output_path)


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
    required=False,
    type=click.Path(exists=False),
    help="Output path. Will be created if it does not exist.",
)
def rationale(file: str, output: Optional[str]):
    """Process the output of the check command and generate a rationale for each match"""
    console = create_console_logger()

    input_file = Path(file)
    output_path = to_output_path(input_file, output)

    add_rationale(console, input_file, output_path)


@click.group(name="namescan")
def main_group():
    """Command Line Interface for MPyL"""


if __name__ == "__main__":
    with redirect_stderr(sys.stdout):
        main_group.help = (
            "Validate an Excel sheet with persons against the Namescan emerald API"
        )
        main_group.add_command(check)
        main_group.add_command(rationale)
        main_group()  # pylint: disable = no-value-for-parameter
