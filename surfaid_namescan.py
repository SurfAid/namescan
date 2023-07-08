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
@click.option(
    "--skip",
    is_flag=True,
    help="Skip the namescan API call and only add the rationale to the output file.",
)
def check(file: str, output: Optional[str], key: str, entity: str, skip: bool):
    """Validate an Excel sheet with persons against the Namescan emerald API."""
    console = create_console_logger()

    input_file = Path(file)
    output_path = to_output_path(input_file, output)

    if not skip:
        validate_file(console, input_file, output_path, key, entity)
    add_rationale(console, input_file, entity, output_path)


if __name__ == "__main__":
    with redirect_stderr(sys.stdout):
        check.help = (
            "Validate an Excel sheet with persons against the Namescan emerald API"
        )
        if len(sys.argv) == 1:
            check.main(["--help"])
        else:
            check()  # pylint: disable=no-value-for-parameter
