import json
import sys
from pathlib import Path

from models import OrganisationScanResult, Gender
from surfaid_namescan import create_console_logger, to_output_path
from tests import test_resource_path
from validate import (
    read_as_dataframe,
    PersonScanResult,
    add_rationale,
    PersonToScan,
    file_response,
)


class TestValidate:
    def test_read_csv_as_dataframe(self):
        dataframe = read_as_dataframe(test_resource_path / "test_namescan.csv")
        first_row = dataframe[0]
        assert len(first_row) == 7

    def test_read_xls_as_dataframe(self):
        dataframe = read_as_dataframe(
            test_resource_path / "PersonBatchSample-input-synthetic.xlsx"
        )
        first_row = dataframe[0]
        assert len(first_row) == 11

    def test_construct_scan_result(self):
        json_string = Path(
            test_resource_path
            / "test_namescan"
            / "f4eb24399e2dc1183eba801996fe7c9f.resp.json"
        ).read_text(encoding="utf-8")

        json_object = json.loads(json_string)
        scan_result = PersonScanResult.from_json(json_object)
        assert scan_result.scan_id == "s12038868"
        assert scan_result.number_of_matches == 23
        assert scan_result.number_of_pep_matches == 4
        assert scan_result.number_of_sip_matches == 19
        first_person = scan_result.entities[0]
        assert first_person.name == "Mohammed Bilal Brigadier General"
        assert first_person.gender == "male"
        assert first_person.citizenship == ""
        reference = first_person.references[0]
        assert reference.name == "CH - SECO Sanction List"
        assert reference.id_in_list == "29902"

    def test_rationale_for_politician(self):
        json_string = Path(test_resource_path / "politician.json").read_text(
            encoding="utf-8"
        )

        json_object = json.loads(json_string)
        scan_result = PersonScanResult.from_json(json_object)
        person = scan_result.entities[0]
        assert person.name == "Dahlan M. Noer"
        summary = "Dahlan M. Noer, male, born 1957-10-10, in Bima"
        assert person.entity_summary == summary
        assert person.politician_summary == f"Politician, {summary}"

    def test_rationale_for_organization(self):
        json_string = Path(test_resource_path / "organization.json").read_text(
            encoding="utf-8"
        )

        json_object = json.loads(json_string)
        scan_result = OrganisationScanResult.from_json(json_object)
        organisation = scan_result.entities[0]
        assert organisation.name == "MAKENGA"
        summary = "MAKENGA"
        assert organisation.entity_summary == summary
        assert organisation.rationale is None

    def test_roundtrip_all_persons(self):
        console = create_console_logger()
        input_file = Path(test_resource_path / "test_namescan.xlsx")
        output_path = to_output_path(input_file, None)
        add_rationale(
            console,
            input_file,
            "person",
            output_path,
            Path(test_resource_path / "test_namescan_explained.xlsx"),
        )

    def test_roundtrip_all_persons_csv(self):
        console = create_console_logger()
        input_file = Path(test_resource_path / "test_namescan.xlsx")
        output_path = to_output_path(input_file, None)
        add_rationale(
            console,
            input_file,
            "person",
            output_path,
            Path(test_resource_path / "test_namescan_explained.csv"),
            file_format=".csv",
        )

    def test_person_to_scan_hash_is_stable(self):
        person = PersonToScan(
            name="Muhammad Ali",
            first_name="Muhammad",
            middle_name=None,
            last_name="Ali",
            gender=Gender("male"),
            dob=None,
            country="Indonesia",
            list_type=None,
            included_lists=None,
            excluded_lists=None,
            match_rate=50,
        )
        assert person.hash == "fded17b8481e0691f4a96e3af2938a41"

    def test_read_response_should_skip_too_old_files(self):
        response = file_response(
            file_path=Path(test_resource_path / "politician.json"), max_days_old=1
        )
        assert response is None

    def test_read_response_should_take_files_not_too_old(self):
        age, response = file_response(
            file_path=Path(test_resource_path / "politician.json"),
            max_days_old=sys.maxsize,
        )
        assert response.json()["scanId"] == "s12022672"
        assert response.json()["date"] == "2023-07-06T19:57:48.2730988+10:00"
        assert age > 0

    def test_date_format(self):
        assert PersonToScan.to_namescan_dob_format(None) == ""
        assert (
            PersonToScan.to_namescan_dob_format("1981-09-21 00:00:00") == "21/09/1981"
        )
        assert PersonToScan.to_namescan_dob_format("21/09/1981") == "21/09/1981"
