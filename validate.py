"""Validation logic for the Namescan emerald API."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
from rich.console import Console


@dataclass
class Person:  # pylint: disable=too-many-instance-attributes
    name: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    gender: Optional[str]
    dob: Optional[str]
    country: Optional[str]
    list_type: Optional[str]
    included_lists: list[str]
    excluded_lists: list[str]
    match_rate: int


def validate_file(console: Console, file: Path, output: Path) -> None:
    """Validate an Excel sheet with persons against the Namescan emerald API."""
    console.log(f"Reading {file}")
    csv = pd.read_csv(file, nrows=10)

    output_path = Path(file.parent, output)
    output_path.mkdir(parents=True, exist_ok=True)

    for line in csv.iterrows():
        console.log(line)
