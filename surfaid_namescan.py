"""Entry point for the surfaid_namescan CLI."""
import sys
from contextlib import redirect_stderr
from pathlib import Path
from typing import Optional, Any

import click
from rich import prompt
from rich.console import Console
from rich.markdown import Markdown

from models import EntityToScan
from validate import (
    validate_file,
    add_rationale,
    check_database,
    read_as_dataframe,
    to_entities,
)

print("Surfaid Namescan CLI © 2023. Starting up...")


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
    type=click.Path(),
    help="Name of output file file. Same as input file name + 'explained' by default.",
)
@click.option(
    "--cache",
    "-c",
    required=False,
    type=click.Path(exists=False),
    help="Path to folder with namescan responses from earlier runs. Same as input file name by default. "
    "Will be created if it does not exist.",
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
    "--age",
    "-a",
    type=click.INT,
    required=False,
    default=90,
    help="The maximum age of namescan data to still be considered valid. Default is 90 days.",
)
@click.option(
    "--skip",
    is_flag=True,
    help="Skip the namescan API call and only add the rationale to the output file.",
)
def check(
    file: str,
    cache: Optional[str],
    output: Optional[str],
    key: str,
    entity: str,
    skip: bool,
    age: int,
):
    """Validate an Excel sheet with persons against the Namescan emerald API."""
    console = create_console_logger()

    input_file = Path(file)
    output_path = to_output_path(input_file, cache)

    file_format = input_file.suffix

    output_sheet = (
        Path(input_file.parent, f"{input_file.stem}-explained{file_format}")
        if not output
        else Path(output)
    )
    if output_sheet.exists() and not prompt.Confirm.ask(
        f"File {output_sheet} already exists. Overwrite?"
    ):
        console.log("Aborting.")
        sys.exit(0)

    console.log(Markdown(f"Reading `{input_file}`"))
    dataframe: list[dict[str, Any]] = read_as_dataframe(input_file)
    entities: list[EntityToScan] = to_entities(entity, dataframe)

    check_database(console, output_path, age, entities)

    if not skip:
        validate_file(console, entities, output_path, key, age)
    add_rationale(console, input_file, entity, output_path, output_sheet, file_format)


if __name__ == "__main__":
    with redirect_stderr(sys.stdout):
        check.help = (
            "Validate an Excel sheet with persons against the Namescan emerald API"
        )
        if len(sys.argv) == 1:
            check.main(["--help"])
        else:
            check()  # pylint: disable=no-value-for-parameter
