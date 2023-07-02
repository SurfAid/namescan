from tests import test_resource_path
from validate import read_as_dataframe


class TestValidate:
    def test_read_csv_as_dataframe(self):
        dataframe = read_as_dataframe(test_resource_path / "test_namescan.csv")
        assert len(dataframe.keys()) == 7

    def test_read_xls_as_dataframe(self):
        dataframe = read_as_dataframe(
            test_resource_path / "PersonBatchSample-input-synthetic.xlsx"
        )
        assert len(dataframe.keys()) == 11
