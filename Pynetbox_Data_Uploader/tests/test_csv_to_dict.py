from unittest.mock import NonCallableMock, patch, MagicMock
from utils.format_dict import FormatDict
import pytest


@pytest.fixture(name="instance")
def instance_fixture():
    netbox = NonCallableMock()
    return FormatDict(netbox)


def test_csv_to_python(instance):
    """
    This test ensures that the csv_read method is called once with the file_path arg.
    """
    file_path = NonCallableMock()
    with patch("utils.format_dict.read_csv") as mock_read_csv:
        res = instance.csv_to_python(file_path)
    mock_read_csv.assert_called_once_with(file_path)
    mock_read_csv.return_value.to_dict.assert_called_once_with(orient="list")
    assert res == mock_read_csv.return_value.to_dict.return_value


def test_separate_data(instance):
    """
    This test ensures that the dictionaries from pandas formatted into row by row dictionaries.
    These are much more understandable and can be used individually or in bulk.
    """
    test_data = {"key1": ["Adata1", "Bdata1"], "key2": ["Adata2", "Bdata2"]}
    format_data = instance.separate_data(test_data)
    assert format_data == [
        {"key1": "Adata1", "key2": "Adata2"},
        {"key1": "Bdata1", "key2": "Bdata2"},
    ]


def test_iterate_dicts_no_items(instance):
    """
    This test ensures that an empty list is returned when there are no dictionaries.
    """
    mock_dictionary = MagicMock()
    with patch("utils.format_dict.FormatDict.format_dict") as mock_format:
        res = instance.iterate_dicts([mock_dictionary])
    mock_format.assert_called_once_with(mock_dictionary)
    assert res == [mock_format.return_value]


def test_iterate_dicts_one_item(instance):
    """
    This test ensures the format method is called on the only dictionary.
    """
    mock_dictionary = MagicMock()
    with patch("utils.format_dict.FormatDict.format_dict") as mock_format:
        res = instance.iterate_dicts([mock_dictionary])
    mock_format.assert_called_once_with(mock_dictionary)
    assert res == [mock_format.return_value]


def test_iterate_dicts_many_items(instance):
    """
    This test ensures the format method is called each dictionary.
    """
    mock_dictionary_1 = MagicMock()
    mock_dictionary_3 = MagicMock()
    mock_dictionary_2 = MagicMock()
    with patch("utils.format_dict.FormatDict.format_dict") as mock_format:
        res = instance.iterate_dicts(
            [mock_dictionary_1, mock_dictionary_2, mock_dictionary_3]
        )
    mock_format.assert_any_call(mock_dictionary_1)
    mock_format.assert_any_call(mock_dictionary_2)
    mock_format.assert_any_call(mock_dictionary_3)
    expected = [
        mock_format.return_value,
        mock_format.return_value,
        mock_format.return_value,
    ]
    assert res == expected
