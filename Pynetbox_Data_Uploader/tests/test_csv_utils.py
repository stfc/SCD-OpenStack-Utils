from unittest.mock import NonCallableMock, patch
from utils.csv_to_dict import CsvUtils
import pytest


@pytest.fixture(name="instance")
def instance_fixture():
    return CsvUtils()


def test_csv_to_python(instance):
    """
    This test ensures that the csv_read method is called once with the file_path arg.
    """
    file_path = NonCallableMock()
    with patch("utils.csv_utils.pd") as mock_dataframe:
        instance.csv_to_python(file_path)
    mock_dataframe.read_csv.assert_called_once_with(file_path)


def test_separate_data(instance):
    """
    This test ensures that the dictionaries from panda formatted into row by row dictionaries.
    These are much more understandable and can be used individually or in bulk.
    """
    test_data = {"key1": ["Adata1", "Bdata1"], "key2": ["Adata2", "Bdata2"]}
    format_data = instance.separate_data(test_data)
    assert format_data == [
        {"key1": "Adata1", "key2": "Adata2"},
        {"key1": "Bdata1", "key2": "Bdata2"},
    ]
