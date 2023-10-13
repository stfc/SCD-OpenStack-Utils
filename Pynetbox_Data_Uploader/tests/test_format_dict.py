from unittest.mock import NonCallableMock, patch, MagicMock
from netbox_api.format_dict import FormatDict
import pytest


@pytest.fixture(name="instance")
def instance_fixture():
    url = NonCallableMock()
    token = NonCallableMock()
    return FormatDict()


def test_iterate_dicts_no_items(instance):
    """
    This test ensures that an empty list is returned when there are no dictionaries.
    """
    mock_dictionary = MagicMock()
    with patch("netbox_api.format_dict.FormatDict.format_dict") as mock_format:
        res = instance.iterate_dicts([mock_dictionary])
    mock_format.assert_called_once_with(mock_dictionary)
    assert res == [mock_format.return_value]


def test_iterate_dicts_one_item(instance):
    """
    This test ensures the format method is called on the only dictionary.
    """
    mock_dictionary = MagicMock()
    with patch("netbox_api.format_dict.FormatDict.format_dict") as mock_format:
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
    with patch("netbox_api.format_dict.FormatDict.format_dict") as mock_format:
        res = instance.iterate_dicts([
            mock_dictionary_1,
            mock_dictionary_2,
            mock_dictionary_3])
    mock_format.assert_any_call(mock_dictionary_1)
    mock_format.assert_any_call(mock_dictionary_2)
    mock_format.assert_any_call(mock_dictionary_3)
    expected = [mock_format.return_value, mock_format.return_value, mock_format.return_value]
    assert res == expected
