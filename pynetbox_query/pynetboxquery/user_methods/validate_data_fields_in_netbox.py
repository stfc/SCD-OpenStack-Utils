from pynetboxquery.utils.parsers import Parsers
from pynetboxquery.netbox_api.validate_data import ValidateData
from pynetboxquery.utils.read_utils.read_file import ReadFile
from pynetboxquery.netbox_api.netbox_connect import api_object


def validate_data_fields_in_netbox(url: str, token: str, file_path: str, **kwargs):
    """
    This function does the following:
    Reads the file from the file path.
    Creates a Pynetbox Api Object with the users credentials.
    Validates all the fields specified by the user
    :param url: The Netbox URL.
    :param token: The users Netbox api token.
    :param file_path: The file_path.
    """
    device_list = ReadFile().read_file(file_path, **kwargs)
    api = api_object(url, token)
    ValidateData().validate_data(device_list, api, kwargs["fields"])


def _parser():
    """
    This function creates the subparser for this user script inheriting the parent parser arguments.
    It also adds an argument to collect the fields specified in the command line.
    """
    parent_parser, main_parser, subparsers = Parsers().arg_parser()
    parser_validate_data_fields_in_netbox = subparsers.add_parser(
        "validate_data_fields_in_netbox",
        description="Check data fields values in Netbox from a file.",
        usage="pynetboxquery validate_data_fields_in_netbox <filepath> <url> <token> <fields=[]>",
        parents=[parent_parser],
        aliases=aliases(),
    )
    parser_validate_data_fields_in_netbox.add_argument(
        "fields", help="The fields to check in Netbox.", nargs="*"
    )
    return main_parser


def aliases():
    """
    This function returns a list of aliases the script should be callable by.
    """
    return ["validate", "validate_data_fields_in_netbox"]


def _collect_args():
    """
    This function calls the parser function and returns the namespace arguments in a dictionary.
    """
    main_parser = _parser()
    return vars(main_parser.parse_args())


def main():
    """
    This function collects the arguments and calls the validate function.
    """
    kwargs = _collect_args()
    validate_data_fields_in_netbox(**kwargs)
