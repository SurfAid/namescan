"""Validation logic for the Namescan emerald API."""
import dataclasses
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import requests
from click import BadParameter
from requests import Response
from rich.console import Console
from rich.markdown import Markdown

from models import (
    EntityToScan,
    OrganizationToScan,
    PersonToScan,
    Entity,
    PersonScanResult,
    OrganisationScanResult,
)

NAME_SCAN_URL = "https://api.namescan.io/v3"
EMERALD_PERSON_URL = f"{NAME_SCAN_URL}/person-scans/emerald"
EMERALD_ORGANIZATION_URL = f"{NAME_SCAN_URL}/organisation-scans/emerald"
REQUEST_TIMEOUT_IN_SECONDS = 10


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
    scan_result = (
        PersonScanResult.from_json(json_object)
        if isinstance(entity, PersonToScan)
        else OrganisationScanResult.from_json(json_object)
    )
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
