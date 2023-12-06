# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
from unittest.mock import patch, NonCallableMock
from pynetboxquery.user_methods.validate_data_fields_in_netbox import Main


def test_aliases():
    """
    This test ensures that the aliases function returns a list of aliases.
    """
    res = Main().aliases()
    assert res == ["validate", "validate_data_fields_in_netbox"]


# pylint: disable = R0801
@patch("pynetboxquery.user_methods.validate_data_fields_in_netbox.Parsers")
def test_subparser(mock_parsers):
    """
    This test ensures all the correct methods are called with the correct arguments to create a subparser.
    """
    mock_subparsers = NonCallableMock()
    mock_parsers.return_value.arg_parser.return_value = (
        "mock_parent_parser",
        "mock_main_parser",
        mock_subparsers,
    )
    res = Main()._subparser()
    mock_parsers.return_value.arg_parser.assert_called_once()
    mock_subparsers.add_parser.assert_called_once_with(
        "validate_data_fields_in_netbox",
        description="Check data fields values in Netbox from a file.",
        usage="pynetboxquery validate_data_fields_in_netbox <filepath> <url> <token> <fields=[]>",
        parents=["mock_parent_parser"],
        aliases=Main().aliases(),
    )
    mock_subparsers.add_parser.return_value.add_argument.assert_called_once_with(
        "fields", help="The fields to check in Netbox.", nargs="*"
    )
    assert res == "mock_main_parser"


@patch("pynetboxquery.user_methods.validate_data_fields_in_netbox.ReadFile")
@patch("pynetboxquery.user_methods.validate_data_fields_in_netbox.api_object")
@patch("pynetboxquery.user_methods.validate_data_fields_in_netbox.ValidateData")
def test_validate_data_fields_in_netbox(
    mock_validate_data, mock_api_object, mock_read_file
):
    """
    This test ensures all the correct methods are called with the correct arguments
    """
    mock_kwargs = {"fields": ["mock_val"]}
    Main()._run("mock_url", "mock_token", "mock_file_path", **mock_kwargs)
    mock_device_list = mock_read_file.return_value.read_file.return_value
    mock_read_file.return_value.read_file.assert_called_once_with(
        "mock_file_path", **mock_kwargs
    )
    mock_api = mock_api_object.return_value
    mock_api_object.assert_called_once_with("mock_url", "mock_token")
    mock_validate_data.return_value.validate_data.assert_called_once_with(
        mock_device_list, mock_api, mock_kwargs["fields"]
    )
