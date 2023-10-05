from unittest.mock import MagicMock, NonCallableMock
from CSV.csv_utils import CsvUtils
import pytest


@pytest.fixture(name="instance")
def instance_fixture():
    return CsvUtils()


def test_csv_to_python(instance):
    mock_dataframe = MagicMock()
    file_path = NonCallableMock()
    instance.pd = mock_dataframe
    instance.csv_to_python(file_path)
    mock_dataframe.read_csv.assert_called_once_with(file_path)



