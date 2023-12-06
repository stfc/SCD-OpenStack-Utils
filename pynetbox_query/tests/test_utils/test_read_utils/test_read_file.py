# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
from unittest.mock import patch
from pytest import raises
from pynetboxquery.utils.read_utils.read_file import ReadFile
from pynetboxquery.utils.error_classes import FileTypeNotSupportedError


def test_read_file_wildcard():
    """
    This test ensures an error is raised when a user supplies an unsupported file type.
    """
    with raises(FileTypeNotSupportedError):
        ReadFile().read_file("mock_file_path.wildcard")


@patch("pynetboxquery.utils.read_utils.read_file.ReadCSV")
def test_read_file_csv(mock_read_csv):
    """
    This test ensures the correct read method is called when supplied with a csv file path.
    """
    res = ReadFile().read_file("mock_file_path.csv")
    mock_read_csv.assert_called_once_with("mock_file_path.csv")
    mock_read_csv.return_value.read.assert_called_once_with()
    assert res == mock_read_csv.return_value.read.return_value


@patch("pynetboxquery.utils.read_utils.read_file.ReadTXT")
def test_read_file_txt(mock_read_txt):
    """
    This test ensures the correct read method is called when supplied with a txt file path.
    """
    res = ReadFile().read_file("mock_file_path.txt")
    mock_read_txt.assert_called_once_with("mock_file_path.txt")
    mock_read_txt.return_value.read.assert_called_once_with()
    assert res == mock_read_txt.return_value.read.return_value


@patch("pynetboxquery.utils.read_utils.read_file.ReadXLSX")
def test_read_file_xlsx(mock_read_xlsx):
    """
    This test ensures the correct read method is called when supplied with a xlsx file path.
    """
    res = ReadFile().read_file("mock_file_path.xlsx")
    mock_read_xlsx.assert_called_once_with("mock_file_path.xlsx")
    mock_read_xlsx.return_value.read.assert_called_once_with()
    assert res == mock_read_xlsx.return_value.read.return_value
