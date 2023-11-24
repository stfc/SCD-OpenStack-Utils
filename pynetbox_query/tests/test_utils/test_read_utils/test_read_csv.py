from unittest.mock import patch
from pynetboxquery.utils.read_utils.read_csv import ReadCSV


@patch("pynetboxquery.utils.read_utils.read_csv.ReadCSV._check_file_path")
@patch("pynetboxquery.utils.read_utils.read_csv.open")
@patch("pynetboxquery.utils.read_utils.read_csv.DictReader")
@patch("pynetboxquery.utils.read_utils.read_csv.list")
@patch("pynetboxquery.utils.read_utils.read_csv.ReadCSV._dict_to_dataclass")
def test_read(
    mock_dict_to_dataclass,
    mock_list,
    mock_dict_reader,
    mock_open_func,
    mock_check_file_path,
):
    """
    This test ensures all calls are made correctly in the read method.
    """
    res = ReadCSV("mock_file_path").read()
    mock_check_file_path.assert_called_once_with("mock_file_path")
    mock_open_func.assert_called_once_with("mock_file_path", mode="r", encoding="UTF-8")
    mock_dict_reader.assert_called_once_with(
        mock_open_func.return_value.__enter__.return_value
    )
    mock_list.assert_called_once_with(mock_dict_reader.return_value)
    mock_dict_to_dataclass.assert_called_once_with(mock_list.return_value)
    assert res == mock_dict_to_dataclass.return_value
