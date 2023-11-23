from unittest.mock import patch, NonCallableMock
from pynetboxquery.user_methods.validate_data_fields_in_netbox import (
    main,
    _collect_args,
    aliases,
    _parser,
    validate_data_fields_in_netbox,
)


@patch(
    "pynetboxquery.user_methods.validate_data_fields_in_netbox.validate_data_fields_in_netbox"
)
@patch("pynetboxquery.user_methods.validate_data_fields_in_netbox._collect_args")
def test_main(mock_collect_args, mock_validate_data_fields_in_netbox):
    main()
    mock_collect_args.assert_called_once()
    mock_validate_data_fields_in_netbox.assert_called_once_with(
        **mock_collect_args.return_value
    )


@patch("pynetboxquery.user_methods.validate_data_fields_in_netbox._parser")
@patch("pynetboxquery.user_methods.validate_data_fields_in_netbox.vars")
def test_collect_args(mock_vars, mock_parser):
    res = _collect_args()
    mock_parser.assert_called_once()
    mock_parser.return_value.parse_args.assert_called_once()
    mock_vars.assery_called_once_with(mock_parser.return_value.parse_args.return_value)
    assert res == mock_vars.return_value


def test_aliases():
    res = aliases()
    assert res == ["validate", "validate_data_fields_in_netbox"]


@patch("pynetboxquery.user_methods.validate_data_fields_in_netbox.Parsers")
def test_parser(mock_parsers):
    mock_subparsers = NonCallableMock()
    mock_parsers.return_value.arg_parser.return_value = (
        "mock_parent_parser",
        "mock_main_parser",
        mock_subparsers,
    )
    res = _parser()
    mock_parsers.return_value.arg_parser.assert_called_once()
    mock_subparsers.add_parser.assert_called_once_with(
        "validate_data_fields_in_netbox",
        description="Check data fields values in Netbox from a file.",
        usage="pynetboxquery validate_data_fields_in_netbox <filepath> <url> <token> <fields=[]>",
        parents=["mock_parent_parser"],
        aliases=aliases(),
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
    mock_kwargs = {"fields": ["mock_val"]}
    validate_data_fields_in_netbox(
        "mock_url", "mock_token", "mock_file_path", **mock_kwargs
    )
    mock_device_list = mock_read_file.return_value.read_file.return_value
    mock_read_file.return_value.read_file.assert_called_once_with(
        "mock_file_path", **mock_kwargs
    )
    mock_api = mock_api_object.return_value
    mock_api_object.assert_called_once_with("mock_url", "mock_token")
    mock_validate_data.return_value.validate_data.assert_called_once_with(
        mock_device_list, mock_api, mock_kwargs["fields"]
    )
