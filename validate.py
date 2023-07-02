"""Validation logic for the Namescan emerald API."""
import dataclasses
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from pandas import Series
from rich.console import Console


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class ListType(str, Enum):
    PEP = "pep"
    SANCTION = "sanction"


@dataclass(frozen=True)
class Person:  # pylint: disable=too-many-instance-attributes
    name: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    gender: Optional[Gender]
    dob: Optional[str]
    country: Optional[str]
    list_type: Optional[ListType]
    included_lists: list[str]
    excluded_lists: list[str]
    match_rate: int = 50

    @staticmethod
    def from_dataframe(framed: Series):
        frame = framed.to_dict()
        gendre = frame.get("Gender", None)
        return Person(
            name=frame.get("Name", None),
            first_name=frame.get("FirstName"),
            middle_name=frame.get("MiddleName"),
            last_name=frame.get("LastName"),
            gender=None if not gendre else Gender(gendre.strip().lower()),
            dob=frame.get("DOB"),
            country=frame.get("Country"),
            list_type=None,
            included_lists=[],
            excluded_lists=[],
            match_rate=50,
        )


def validate_file(console: Console, file: Path, output: Path) -> None:
    """Validate an Excel sheet with persons against the Namescan emerald API."""
    console.log(f"Reading {file}")
    extension = file.suffix
    dataframe = (
        pd.read_csv(file, nrows=10) if extension == ".csv" else pd.read_excel(file)
    ).replace(np.nan, None)

    output_path = Path(file.parent, output)
    output_path.mkdir(parents=True, exist_ok=True)

    for _, row in dataframe.iterrows():
        person = Person.from_dataframe(row)
        json_foo = json.dumps(dataclasses.asdict(person))
        console.log(json_foo)
