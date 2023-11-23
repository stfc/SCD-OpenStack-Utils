from unittest.mock import patch
from pytest import raises
from pynetboxquery.utils.read_utils.read_file import ReadFile
from pynetboxquery.utils.error_classes import FileTypeNotSupportedError


def test_read_file_wildcard():
    with raises(FileTypeNotSupportedError):
        ReadFile().read_file("mock_file_path.wildcard")


@patch("pynetboxquery.utils.read_utils.read_file.ReadCSV")
def test_read_file_csv(mock_read_csv):
    res = ReadFile().read_file("mock_file_path.csv")
    mock_read_csv.assert_called_once_with("mock_file_path.csv")
    mock_read_csv.return_value.read.assert_called_once_with()
    assert res == mock_read_csv.return_value.read.return_value


@patch("pynetboxquery.utils.read_utils.read_file.ReadTXT")
def test_read_file_txt(mock_read_txt):
    res = ReadFile().read_file("mock_file_path.txt")
    mock_read_txt.assert_called_once_with("mock_file_path.txt")
    mock_read_txt.return_value.read.assert_called_once_with()
    assert res == mock_read_txt.return_value.read.return_value


@patch("pynetboxquery.utils.read_utils.read_file.ReadXLSX")
def test_read_file_xlsx(mock_read_xlsx):
    res = ReadFile().read_file("mock_file_path.xlsx")
    mock_read_xlsx.assert_called_once_with("mock_file_path.xlsx")
    mock_read_xlsx.return_value.read.assert_called_once_with()
    assert res == mock_read_xlsx.return_value.read.return_value
