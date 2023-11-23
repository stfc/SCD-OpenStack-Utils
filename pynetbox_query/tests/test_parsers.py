from pytest import fixture
from unittest.mock import patch
from pynetboxquery.utils.parsers import Parsers


@fixture(name="instance")
def instance_fixture():
    return Parsers()


@patch("pynetboxquery.utils.parsers.Parsers._parent_parser")
@patch("pynetboxquery.utils.parsers.argparse")
def test_arg_parser(mock_argparse, mock_parent_parser, instance):
    """
    This test ensures the argparse method adds the correct arguments and returns them.
    """
    res = instance.arg_parser()
    mock_parent_parser.assert_called_once_with()
    mock_argparse.ArgumentParser.assert_called_once_with(
        description="The main command. This cannot be run standalone and requires a subcommand to be provided.",
        usage="pynetboxquery [command] [filepath] [url] [token] [kwargs]",
    )
    mock_argparse.ArgumentParser.return_value.add_subparsers.assert_called_once_with(
        dest="subparsers",
    )
    expected_parent = mock_parent_parser.return_value
    expected_main = mock_argparse.ArgumentParser.return_value
    expected_subparser = (
        mock_argparse.ArgumentParser.return_value.add_subparsers.return_value
    )
    assert res == (expected_parent, expected_main, expected_subparser)


@patch("pynetboxquery.utils.parsers.argparse")
def test_parent_parser(mock_argparse, instance):
    res = instance._parent_parser()
    mock_argparse.ArgumentParser.assert_called_once_with(add_help=False)
    mock_parent_parser = mock_argparse.ArgumentParser.return_value
    mock_parent_parser.add_argument.assert_any_call("url", help="The Netbox URL.")
    mock_parent_parser.add_argument.assert_any_call("token", help="Your Netbox Token.")
    mock_parent_parser.add_argument.assert_any_call(
        "file_path", help="Your file path to csv files."
    )
    mock_parent_parser.add_argument.assert_any_call(
        "--delimiter", help="The separator in the text file."
    )
    mock_parent_parser.add_argument.assert_any_call(
        "--sheet-name", help="The sheet in the Excel Workbook to read from."
    )
    assert res == mock_parent_parser
