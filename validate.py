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
class DateOfBirth:
    date: str


@dataclass(frozen=True)
class Reference:
    name: str
    id_in_list: str


@dataclass(frozen=True)
class OtherName:
    name: str
    type: str


@dataclass(frozen=True)
class Person:  # pylint: disable=too-many-instance-attributes
    update_at: Optional[str]
    category: str
    name: str
    gender: str
    original_script_name: Optional[str]
    dates_of_birth: list[DateOfBirth]
    reference_type: str
    references: list[Reference]
    program: Optional[str]
    nationality: str
    citizenship: str
    other_names: list[OtherName]
    summary: Optional[str]
    match_rate: float

    @staticmethod
    def from_json(person: dict):
        return Person(
            update_at=person.get("update_at", None),
            category=person["category"],
            name=person["name"],
            gender=person["gender"],
            original_script_name=person.get("original_script_name"),
            dates_of_birth=[
                DateOfBirth(date=dob["date"])
                for dob in person.get("dates_of_birth", [])
            ],
            reference_type=person["reference_type"],
            references=[
                Reference(name=ref["name"], id_in_list=ref["id_in_list"])
                for ref in person.get("references", [])
            ],
            program=person.get("program", None),
            nationality=person["nationality"],
            citizenship=person["citizenship"],
            other_names=[
                OtherName(name=other_name["name"], type=other_name["type"])
                for other_name in person.get("other_names", [])
            ],
            summary=person.get("summary", None),
            match_rate=person["match_rate"],
        )


@dataclass(frozen=True)
class ScanResult:
    date: str
    scan_id: str
    number_of_matches: int
    number_of_pep_matches: int
    number_of_sip_matches: int
    persons: list[Person]

    @staticmethod
    def from_json(data: dict):
        return ScanResult(
            date=data["date"],
            scan_id=data["scan_id"],
            number_of_matches=data["number_of_matches"],
            number_of_pep_matches=data["number_of_pep_matches"],
            number_of_sip_matches=data["number_of_sip_matches"],
            persons=[Person.from_json(person) for person in data["persons"]],
        )


@dataclass(frozen=True)
class PersonToScan:  # pylint: disable=too-many-instance-attributes
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
        return PersonToScan(
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
    console: Console, person: PersonToScan, key: str, index: str, output_path: Path
) -> None:
    """Send a request to the Namescan emerald API."""
    console.log(f"Sending request to Namescan API for {person.name}...")
    person_dict = dataclasses.asdict(person)
    log_request(person_dict, Path(output_path, f"{index}.req.json"))

    output_file = Path(output_path, f"{index}.resp.json")
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
    return (pd.read_csv(file) if extension == ".csv" else pd.read_excel(file)).replace(
        np.nan, None
    )


def validate_file(console: Console, file: Path, output: Path, key: str) -> None:
    """Validate an Excel sheet with persons against the Namescan emerald API."""
    console.log(f"Reading {file}")
    dataframe = read_as_dataframe(file)

    output_path = Path(file.parent, output)
    output_path.mkdir(parents=True, exist_ok=True)

    for index, row in dataframe.iterrows():
        person = PersonToScan.from_dataframe(row)
        send_request(console, person, key, str(index), output_path)
