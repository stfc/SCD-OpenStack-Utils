from pynetboxquery.utils.parsers import arg_parser
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


def collect_args():
    parser = arg_parser()
    parser.add_argument("fields", help="The fields to check in Netbox.", nargs="*")
    return vars(parser.parse_args())


def main():
    kwargs = collect_args()
    validate_data_fields_in_netbox(**kwargs)


if __name__ == "__main__":
    main()
