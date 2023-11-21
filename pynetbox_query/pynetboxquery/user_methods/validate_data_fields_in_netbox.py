from pynetboxquery.utils.parsers import Parsers
from pynetboxquery.netbox_api.validate_data import ValidateData
from pynetboxquery.utils.read_data import ReadData
from pynetboxquery.netbox_api.netbox_connect import api_object


def validate_data_fields_in_netbox(url: str, token: str, file_path: str, **kwargs):
    """
    This method will iterate through a csv.
    Check that each device exists in netbox.
    For each device print: Device {name} exists in Netbox: {bool}.
    :param url: The Netbox URL.
    :param token: The users Netbox api token.
    :param file_path: The file_path.
    """
    device_list = ReadData().read(file_path, **kwargs)
    api = api_object(url, token)
    ValidateData().validate_data(device_list, api, kwargs["fields"])


def _validate_parser():
    parent_parser, main_parser, subparsers = Parsers().arg_parser()
    parser_validate_data_fields_in_netbox = subparsers.add_parser(
        "validate_data_fields_in_netbox",
        description="Check data fields values in Netbox from a file.",
        usage="pynetboxquery validate_data_fields_in_netbox <filepath> <url> <token> <fields=[]>",
        parents=[parent_parser],
        aliases=["validate"],
    )
    parser_validate_data_fields_in_netbox.add_argument(
        "fields", help="The fields to check in Netbox.", nargs="*"
    )
    # TODO
    # parser_validate_data_fields_in_netbox.add_argument(
    #     "--short",
    #     type=bool,
    #     help="To include all results or only bad results from Netbox.",
    #     dest="TRUE/FALSE",
    # )
    return main_parser


def _collect_args():
    main_parser = _validate_parser()
    return vars(main_parser.parse_args())


def main_validate_data_fields_in_netbox():
    kwargs = _collect_args()
    validate_data_fields_in_netbox(**kwargs)

