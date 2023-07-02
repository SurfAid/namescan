"""Validation logic for the Namescan emerald API."""
import dataclasses
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import requests
from pandas import Series
from rich.console import Console


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class ListType(str, Enum):
    PEP = "pep"
    SANCTION = "sanction"


NAME_SCAN_URL = "https://api.namescan.io/v2"
EMERALD_URL = f"{NAME_SCAN_URL}/person-scans/emerald"
REQUEST_TIMEOUT_IN_SECONDS = 10


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
    included_lists: Optional[str]
    excluded_lists: Optional[str]
    match_rate: int = 50

    @staticmethod
    def from_dataframe(framed: Series):
        frame = framed.to_dict()
        gender = frame.get("Gender", None)
        return Person(
            name=frame.get("Name", None),
            first_name=frame.get("FirstName"),
            middle_name=frame.get("MiddleName"),
            last_name=frame.get("LastName"),
            gender=None if not gender else Gender(gender.strip().lower()),
            dob=frame.get("DOB"),
            country=frame.get("Country"),
            list_type=None,
            included_lists=None,
            excluded_lists=None,
            match_rate=50,
        )


def log_request(request_body: dict, output_file: Path):
    """Log a request to a file."""
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(json.dumps(request_body, indent=4))


def send_request(
    console: Console, person: Person, key: str, index: str, output_path: Path
) -> None:
    """Send a request to the Namescan emerald API."""
    console.log(f"Sending request to Namescan API for {person.name}...")
    person_dict = dataclasses.asdict(person)
    log_request(person_dict, Path(output_path, f"{index}.req.json"))

    output_file = Path(output_path, Path(output_path, f"{index}.resp.json"))
    if not output_file.exists():
        response = requests.post(
            EMERALD_URL,
            json=person_dict,
            headers={"api-key": key},
            timeout=REQUEST_TIMEOUT_IN_SECONDS,
        )
        if response.status_code < 300:
            log_request(response.json(), output_file)
        else:
            console.log(
                f"[red]Error while sending request to Namescan API: {response.status_code} - {response.text}[/red]"
            )


def read_as_dataframe(file: Path) -> pd.DataFrame:
    extension = file.suffix
    return (
        pd.read_csv(file, nrows=10) if extension == ".csv" else pd.read_excel(file)
    ).replace(np.nan, None)


def validate_file(console: Console, file: Path, output: Path, key: str) -> None:
    """Validate an Excel sheet with persons against the Namescan emerald API."""
    console.log(f"Reading {file}")
    dataframe = read_as_dataframe(file)

    output_path = Path(file.parent, output)
    output_path.mkdir(parents=True, exist_ok=True)

    for index, row in dataframe.iterrows():
        person = Person.from_dataframe(row)
        send_request(console, person, key, str(index), output_path)
