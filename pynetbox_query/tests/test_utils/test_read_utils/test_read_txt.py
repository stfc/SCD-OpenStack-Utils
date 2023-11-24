from unittest.mock import patch
from pytest import raises
from pynetboxquery.utils.read_utils.read_txt import ReadTXT
from pynetboxquery.utils.error_classes import DelimiterNotSpecifiedError


@patch("pynetboxquery.utils.read_utils.read_txt.ReadTXT._check_file_path")
@patch("pynetboxquery.utils.read_utils.read_txt.open")
@patch("pynetboxquery.utils.read_utils.read_txt.DictReader")
@patch("pynetboxquery.utils.read_utils.read_txt.list")
@patch("pynetboxquery.utils.read_utils.read_txt.ReadTXT._dict_to_dataclass")
def test_read(
    mock_dict_to_dataclass, mock_list, mock_dict_reader, mock_open, mock_check_file_path
):
    """
    This test ensures all calls are made correctly in the read method.
    """
    res = ReadTXT("mock_file_path", **{"delimiter": ","}).read()
    mock_check_file_path.assert_called_once_with("mock_file_path")
    mock_open.assert_called_once_with("mock_file_path", mode="r", encoding="UTF-8")
    mock_dict_reader.assert_called_once_with(
        mock_open.return_value.__enter__.return_value, delimiter=","
    )
    mock_list.assert_called_once_with(mock_dict_reader.return_value)
    mock_dict_to_dataclass.assert_called_once_with(mock_list.return_value)
    assert res == mock_dict_to_dataclass.return_value


def test_validate():
    """
    This test ensures the validate method is called and doesn't error for a correct case.
    """
    ReadTXT("", **{"delimiter": ","})


def test_validate_fail():
    """
    This test ensures the validate method is called and does error for an incorrect case.
    """
    with raises(DelimiterNotSpecifiedError):
        ReadTXT("")
