from unittest.mock import patch
from pynetbox_query.argparser import arg_parser


@patch("pynetbox_query.argparser.argparse.ArgumentParser")
def test_arg_parser(mock_argparse):
    """
    This test ensures the argparse method adds the correct arguments and returns them.
    """
    res = arg_parser()
    mock_argparse.assert_called_once_with(
        description="Create devices in Netbox from CSV files.",
        usage="python csv_to_netbox.py url token file_path",
    )
    mock_argparse.return_value.add_argument.assert_any_call(
        "file_path", help="Your file path to csv files."
    )
    mock_argparse.return_value.add_argument.assert_any_call(
        "token", help="Your Netbox Token."
    )
    mock_argparse.return_value.add_argument.assert_any_call(
        "url", help="The Netbox URL."
    )
    mock_argparse.return_value.parse_args.assert_called()
    assert res == mock_argparse.return_value.parse_args()
