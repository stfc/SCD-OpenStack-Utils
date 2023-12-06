# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
from unittest.mock import patch
from pytest import raises
from pynetboxquery.utils.read_utils.read_xlsx import ReadXLSX
from pynetboxquery.utils.error_classes import SheetNameNotSpecifiedError


def test_validate():
    """
    This test ensures the validate method is called and doesn't error for a correct case.
    """
    ReadXLSX("", **{"sheet_name": "test"})


def test_validate_fail():
    """
    This test ensures the validate method is called and does error for an incorrect case.
    """
    with raises(SheetNameNotSpecifiedError):
        ReadXLSX("")


@patch("pynetboxquery.utils.read_utils.read_xlsx.ReadXLSX._check_file_path")
@patch("pynetboxquery.utils.read_utils.read_xlsx.read_excel")
@patch("pynetboxquery.utils.read_utils.read_xlsx.ReadXLSX._dict_to_dataclass")
def test_read(mock_dict_to_dataclass, mock_read_excel, mock_check_file_path):
    """
    This test ensures all calls are made correctly in the read method.
    """
    res = ReadXLSX("mock_file_path", **{"sheet_name": "test"}).read()
    mock_check_file_path.assert_called_once_with("mock_file_path")
    mock_read_excel.assert_called_once_with("mock_file_path", sheet_name="test")
    mock_dataframe = mock_read_excel.return_value
    mock_dataframe.to_dict.assert_called_once_with(orient="records")
    mock_dictionary_list = mock_dataframe.to_dict.return_value
    mock_dict_to_dataclass.assert_called_once_with(mock_dictionary_list)
    mock_device_list = mock_dict_to_dataclass.return_value
    assert res == mock_device_list
