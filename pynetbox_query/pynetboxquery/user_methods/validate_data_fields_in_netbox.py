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
