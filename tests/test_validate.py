from surfaid_namescan import create_console_logger
from tests import test_resource_path
from validate import validate_file


class TestValidate:

    def test_validate(self):
        console = create_console_logger()
        validate_file(console, test_resource_path / "test_namescan.csv")
