from pathlib import Path

from surfaid_namescan import create_console_logger
from tests import test_resource_path
from validate import validate_file


class TestValidate:
    def test_validate(self):
        console = create_console_logger()
        validate_file(console, test_resource_path / "test_namescan.csv", Path("output"))

    def test_validate_xls(self):
        console = create_console_logger()
        validate_file(
            console,
            test_resource_path / "PersonBatchSample-input-synthetic.xlsx",
            Path("output"),
        )
