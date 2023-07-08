"""Validation logic for the Namescan emerald API."""
import dataclasses
import hashlib
import json
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import requests
from click import BadParameter
from pandas import Series
from requests import Response
from rich.console import Console
from rich.markdown import Markdown


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class ListType(str, Enum):
    PEP = "pep"
    SANCTION = "sanction"


NAME_SCAN_URL = "https://api.namescan.io/v2"
EMERALD_PERSON_URL = f"{NAME_SCAN_URL}/person-scans/emerald"
EMERALD_ORGANIZATION_URL = f"{NAME_SCAN_URL}/organisation-scans/emerald"
REQUEST_TIMEOUT_IN_SECONDS = 10


@dataclass(frozen=True)
class DateOfBirth:
    date: str


@dataclass(frozen=True)
class Reference:
    name: str
    id_in_list: Optional[str]


@dataclass(frozen=True)
class OtherName:
    name: str
    type: str


@dataclass(frozen=True)
class PoliticalParty:
    title: str


@dataclass(frozen=True)
class Role:
    title: str


@dataclass(frozen=True)
class PlaceOfBirth:
    location: str
    country: Optional[str]


@dataclass(frozen=True)
class Entity:
    name: str

    @property
    @abstractmethod
    def rationale(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def entity_summary(self) -> str:
        pass


@dataclass(frozen=True, eq=True)
class Person(Entity):  # pylint: disable=too-many-instance-attributes
    update_at: Optional[str]
    category: str
    name: str
    deceased: bool
    deceased_date: Optional[str]
    gender: Optional[Gender]
    original_script_name: Optional[str]
    dates_of_birth: list[DateOfBirth]
    places_of_birth: list[PlaceOfBirth]
    reference_type: str
    references: list[Reference]
    program: Optional[str]
    occupations: list[str]
    political_parties: list[PoliticalParty]
    roles: list[Role]
    nationality: str
    citizenship: str
    other_names: list[OtherName]
    summary: Optional[str]
    match_rate: float

    @property
    def rationale(self) -> Optional[str]:  # pylint: disable=too-many-return-statements
        if self.deceased:
            return f"Deceased {self.deceased_date}"

        if self.original_script_name:
            return f"Not an Indonesian name: {self.original_script_name}"

        if self.program and "syr" in self.program.lower():
            return "Suspect in Syrian conflict"

        if "politician" in self.occupations:
            return self.politician_summary

        if self.roles:
            return f"Public figure: {self.roles[0].title}"

        if self.citizenship != "" and "indonesia" not in self.citizenship.lower():
            return f"Foreigner: {self.citizenship}"

        return None

    @property
    def politician_summary(self):
        summary = self.entity_summary
        affiliation = (
            f" for {self.political_parties[0].title}" if self.political_parties else ""
        )
        return f"Politician, {summary}{affiliation}"

    @property
    def entity_summary(self):
        if self.summary:
            return self.summary

        name = (
            ", ".join([other.name for other in self.other_names])
            if self.other_names
            else self.name
        )
        origin = (
            f", in {self.places_of_birth[0].location}" if self.places_of_birth else ""
        )
        born = f", born {self.dates_of_birth[0].date}" if self.dates_of_birth else ""
        gender = f", {self.gender.value}" if self.gender else ""
        return f"{name}{gender}{born}{origin}"

    def __hash__(self):
        return hash(tuple(self.references))

    @staticmethod
    def from_json(person: dict):
        gender = person.get("gender", None)
        return Person(
            update_at=person.get("update_at", None),
            category=person["category"],
            name=person["name"],
            deceased=person.get("deceased", False),
            deceased_date=person.get("deceased_date"),
            gender=None if not gender else Gender(gender.strip().lower()),
            original_script_name=person.get("original_script_name"),
            dates_of_birth=[
                DateOfBirth(date=dob["date"])
                for dob in person.get("dates_of_birth", [])
            ],
            places_of_birth=[
                PlaceOfBirth(
                    location=pob.get("location", ""), country=pob.get("country")
                )
                for pob in person.get("places_of_birth", [])
            ],
            reference_type=person["reference_type"],
            references=[
                Reference(name=ref["name"], id_in_list=ref.get("id_in_list"))
                for ref in person.get("references", [])
            ],
            program=person.get("program", None),
            occupations=person.get("occupations", []),
            political_parties=[
                PoliticalParty(title=party["title"])
                for party in person.get("political_parties", [])
            ],
            roles=[Role(title=role["title"]) for role in person.get("roles", [])],
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


@dataclass(frozen=True)
class PersonScanResult(ScanResult):
    persons: list[Person]

    @staticmethod
    def from_json(data: dict):
        return PersonScanResult(
            date=data["date"],
            scan_id=data["scan_id"],
            number_of_matches=data["number_of_matches"],
            number_of_pep_matches=data["number_of_pep_matches"],
            number_of_sip_matches=data["number_of_sip_matches"],
            persons=[Person.from_json(person) for person in data.get("persons", [])],
        )


@dataclass(frozen=True)
class EntityToScan:
    name: str
    country: str

    @property
    @abstractmethod
    def hash(self) -> str:
        pass


@dataclass(frozen=True)
class OrganizationToScan(EntityToScan):
    name: str
    country: str

    @property
    def hash(self) -> str:
        joined = "".join([self.name, self.country])
        return hashlib.md5(joined.encode("utf-8")).hexdigest()

    @staticmethod
    def from_dataframe(frame: Series):
        return OrganizationToScan(name=frame["Name"], country=frame["Country"])


@dataclass(frozen=True)
class PersonToScan(EntityToScan):  # pylint: disable=too-many-instance-attributes
    name: str
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    gender: Optional[Gender]
    dob: Optional[str]
    country: str
    list_type: Optional[ListType]
    included_lists: Optional[str]
    excluded_lists: Optional[str]
    match_rate: int = 50

    @property
    def hash(self) -> str:
        joined = "".join(
            [
                self.name,
                self.dob or "",
                self.first_name or "",
                self.last_name or "",
                self.gender or "",
            ]
        )
        return hashlib.md5(joined.encode("utf-8")).hexdigest()

    @staticmethod
    def from_dataframe(frame: Series):
        frame_dict = frame.to_dict()
        gender = frame_dict.get("Gender", None)
        return PersonToScan(
            name=frame_dict["Name"],
            first_name=frame_dict.get("FirstName"),
            middle_name=frame_dict.get("MiddleName"),
            last_name=frame_dict.get("LastName"),
            gender=None if not gender else Gender(gender.strip().lower()),
            dob=frame_dict.get("DOB"),
            country=frame_dict.get("Country", "Indonesia"),
            list_type=None,
            included_lists=None,
            excluded_lists=None,
            match_rate=50,
        )


def log_request(request_body: dict, output_file: Path):
    """Log a request to a file."""
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(json.dumps(request_body, indent=4))


def file_response(file_path: Path) -> Response:
    response = Response()
    response.status_code = 201
    response._content = bytes(  # pylint: disable=protected-access
        file_path.read_text("utf-8"), "utf-8"
    )
    return response


def send_request(
    console: Console,
    entity: EntityToScan,
    index: str,
    api_url: str,
    entity_dict: dict,
    key: str,
    output_path: Path,
) -> None:
    """Send a request to the Namescan emerald API."""
    status_prefix = f"{index} checking {entity.name}..."
    with console.status(status_prefix) as status:
        log_request(entity_dict, Path(output_path, f"{entity.hash}.req.json"))
        output_file = Path(output_path, f"{entity.hash}.resp.json")
        response = (
            requests.post(
                api_url,
                json=entity_dict,
                headers={"api-key": key},
                timeout=REQUEST_TIMEOUT_IN_SECONDS,
            )
            if not output_file.exists()
            else file_response(output_file)
        )
        if response.status_code < 300:
            response_json = response.json()
            status.console.log(
                f"{index} checked {entity.name} - {response_json.get('number_of_matches', 'Error')} matches"
            )
            log_request(response_json, output_file)
        else:
            console.log(
                f"[red]Error while sending request {entity.hash}, {entity.name} to Namescan API: {response.status_code}"
                f" - {response.text}[/red]"
            )


def read_as_dataframe(file: Path) -> pd.DataFrame:
    extension = file.suffix
    return (pd.read_csv(file) if extension == ".csv" else pd.read_excel(file)).replace(
        np.nan, None
    )


def validate_file(
    console: Console, file: Path, output_path: Path, key: str, entity: str
) -> None:
    """Validate an Excel sheet with persons against the Namescan emerald API."""
    console.log(Markdown(f"Reading `{file}`"))
    dataframe = read_as_dataframe(file)

    output_path.mkdir(parents=True, exist_ok=True)

    for index, row in dataframe.iterrows():
        if entity == "organization":
            org = OrganizationToScan.from_dataframe(row)
            send_request(
                console,
                org,
                str(index),
                EMERALD_ORGANIZATION_URL,
                dataclasses.asdict(org),
                key,
                output_path,
            )
        elif entity == "person":
            person = PersonToScan.from_dataframe(row)
            send_request(
                console,
                person,
                str(index),
                EMERALD_PERSON_URL,
                dataclasses.asdict(person),
                key,
                output_path,
            )
        else:
            raise BadParameter(f"Unknown scan type: {entity}")


@dataclass(frozen=True)
class Rationale:
    entity_to_scan: EntityToScan
    matches_with_explanations: dict[Entity, Optional[str]]

    @property
    def matches(self) -> int:
        return len(self.matches_with_explanations.keys())

    @property
    def explained(self) -> int:
        return len(
            [
                explanation
                for explanation in self.matches_with_explanations.values()
                if explanation is not None
            ]
        )

    @property
    def rationale(self):
        return ", ".join(
            [
                f"{entity.name}: {explanation}"
                for entity, explanation in self.matches_with_explanations.items()
                if explanation is not None
            ]
        )

    @property
    def no_rationale(self):
        return ", ".join(
            [
                f"{entity.name}: {entity.entity_summary}"
                for entity, explanation in self.matches_with_explanations.items()
                if explanation is None
            ]
        )

    @property
    def icon(self):
        return "🟢" if self.matches == self.explained else "🔴"


def add_rationale(
    console: Console,
    input_file: Path,
    entity: str,
    output_path: Path,
    file_format: str = "xlsx",
) -> None:
    output_sheet = Path(output_path, f"{input_file.stem}-explained.{file_format}")
    console.log(Markdown(f"Writing `{output_sheet}`"))
    dataframe = read_as_dataframe(input_file)

    entities = [
        (
            index,
            PersonToScan.from_dataframe(row)
            if entity == "person"
            else OrganizationToScan.from_dataframe(row),
        )
        for index, row in dataframe.iterrows()
    ]

    rationales: list[Rationale] = [
        create_rationale(
            console,
            str(index),
            entity,
            entity.hash,
            output_path,
        )
        for index, entity in entities
    ]

    def to_verdict(rationale: Rationale) -> str:
        if rationale.explained == rationale.matches:
            return "False positive"
        if rationale.matches == 0:
            return "No match"
        return "Needs explanation"

    with_explanations = dataframe.assign(
        UniqueId=[rationale.entity_to_scan.hash for rationale in rationales],
        Matched=[rationale.matches > 0 for rationale in rationales],
        Verdict=[to_verdict(rationale) for rationale in rationales],
        Explanation=[rationale.rationale for rationale in rationales],
        NeedExplanation=[rationale.no_rationale for rationale in rationales],
    )
    with_explanations.to_excel(  # pylint: disable=expression-not-assigned
        output_sheet, index=True
    ) if file_format == "xlsx" else with_explanations.to_csv(output_sheet, index=True)
    total_matches = sum(rationale.matches for rationale in rationales)
    total_explained = sum(rationale.explained for rationale in rationales)
    console.log(f"Total matches: {total_matches}, total explained: {total_explained}")


def create_rationale(
    console: Console,
    index: str,
    entity: EntityToScan,
    person_hash: str,
    output_path: Path,
) -> Rationale:
    response_json_string = Path(output_path, f"{person_hash}.resp.json").read_text(
        encoding="utf-8"
    )
    json_object = json.loads(response_json_string)
    scan_result = PersonScanResult.from_json(json_object)
    rationale = Rationale(
        entity_to_scan=entity,
        matches_with_explanations={
            match: match.rationale for match in scan_result.persons
        },
    )
    console.log(
        f"{rationale.icon} {index} {entity.name} -> {rationale.matches} matches,"
        f" {rationale.explained} false positive."
    )
    return rationale
