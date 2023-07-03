import json
from pathlib import Path

from tests import test_resource_path
from validate import read_as_dataframe, ScanResult


class TestValidate:
    def test_read_csv_as_dataframe(self):
        dataframe = read_as_dataframe(test_resource_path / "test_namescan.csv")
        assert len(dataframe.keys()) == 7

    def test_read_xls_as_dataframe(self):
        dataframe = read_as_dataframe(
            test_resource_path / "PersonBatchSample-input-synthetic.xlsx"
        )
        assert len(dataframe.keys()) == 11

    def test_construct_scan_result(self):
        json_string = Path(test_resource_path / "output" / "1.resp.json").read_text(
            encoding="utf-8"
        )

        json_object = json.loads(json_string)
        scan_result = ScanResult.from_json(json_object)
        assert scan_result.scan_id == "s11994383"
        assert scan_result.number_of_matches == 1
        assert scan_result.number_of_pep_matches == 0
        assert scan_result.number_of_sip_matches == 1
        first_person = scan_result.persons[0]
        assert first_person.name == "Dr. Malek Ali"
        assert first_person.gender == "male"
        assert first_person.citizenship == ""
        reference = first_person.references[0]
        assert reference.name == "CH - SECO Sanction List"
        assert reference.id_in_list == "28051"
