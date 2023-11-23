from dataclasses import asdict
from unittest.mock import patch, NonCallableMock
from pynetboxquery.user_methods.upload_devices_to_netbox import (
    main,
    aliases,
    _collect_args,
    _parser,
    run,
)


# pylint: disable = R0801
@patch("pynetboxquery.user_methods.upload_devices_to_netbox.upload_devices_to_netbox")
@patch("pynetboxquery.user_methods.upload_devices_to_netbox._collect_args")
def test_main(mock_collect_args, mock_upload_devices_to_netbox):
    """
    This test ensures all the correct methods are called.
    """
    main()
    mock_collect_args.assert_called_once()
    mock_upload_devices_to_netbox.assert_called_once_with(
        **mock_collect_args.return_value
    )


@patch("pynetboxquery.user_methods.upload_devices_to_netbox._parser")
@patch("pynetboxquery.user_methods.upload_devices_to_netbox.vars")
def test_collect_args(mock_vars, mock_parser):
    """
    This test ensures all the correct methods are called.
    """
    res = _collect_args()
    mock_parser.assert_called_once()
    mock_parser.return_value.parse_args.assert_called_once()
    mock_vars.assery_called_once_with(mock_parser.return_value.parse_args.return_value)
    assert res == mock_vars.return_value


def test_aliases():
    """
    This test ensures that the aliases function returns a list of aliases.
    """
    res = aliases()
    assert res == ["create", "create_devices"]


@patch("pynetboxquery.user_methods.upload_devices_to_netbox.Parsers")
def test_parser(mock_parsers):
    """
    This test ensures all the correct methods are called with the correct arguments to create a subparser.
    """
    mock_subparsers = NonCallableMock()
    mock_parsers.return_value.arg_parser.return_value = (
        "mock_parent_parser",
        "mock_main_parser",
        mock_subparsers,
    )
    res = _parser()
    mock_parsers.return_value.arg_parser.assert_called_once()
    mock_subparsers.add_parser.assert_called_once_with(
        "create_devices",
        description="Create devices in Netbox from a file.",
        usage="pynetboxquery create_devices <filepath> <url> <token> <options>",
        parents=["mock_parent_parser"],
        aliases=["create"],
    )
    assert res == "mock_main_parser"


@patch("pynetboxquery.user_methods.upload_devices_to_netbox.ReadFile")
@patch("pynetboxquery.user_methods.upload_devices_to_netbox.api_object")
@patch("pynetboxquery.user_methods.upload_devices_to_netbox.ValidateData")
@patch("pynetboxquery.user_methods.upload_devices_to_netbox.QueryDevice")
@patch("pynetboxquery.user_methods.upload_devices_to_netbox.NetboxCreate")
def test_upload_devices_to_netbox(
    mock_netbox_create, mock_query_device, mock_validate_data, mock_api, mock_read_file
):
    """
    This test ensures all the correct methods are called with the correct arguments
    """
    run("mock_url", "mock_token", "mock_file_path")
    mock_api_object = mock_api.return_value
    mock_api.assert_called_once_with("mock_url", "mock_token")
    mock_device_list = mock_read_file.return_value.read_file.return_value
    mock_read_file.return_value.read_file.assert_called_once_with("mock_file_path")
    mock_validate_data.return_value.validate_data.assert_called_once_with(
        mock_device_list, mock_api_object, **{"fields": ["name", "device_type"]}
    )
    mock_queried_devices = mock_query_device.return_value.query_list.return_value
    mock_query_device.assert_called_once_with(mock_api_object)
    mock_query_device.return_value.query_list.assert_called_once_with(mock_device_list)
    mock_dictionary_devices = [
        asdict(mock_device) for mock_device in mock_queried_devices
    ]
    mock_netbox_create.assert_called_once_with(mock_api_object)
    mock_netbox_create.return_value.create_device.assert_called_once_with(
        mock_dictionary_devices
    )
