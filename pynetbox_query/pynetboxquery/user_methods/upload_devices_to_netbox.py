import sys
from dataclasses import asdict
from pynetboxquery.utils.read_data import ReadData
from pynetboxquery.netbox_api.validate_data import ValidateData
from pynetboxquery.utils.query_device import QueryDevice
from pynetboxquery.netbox_api.netbox_create import NetboxCreate
from pynetboxquery.netbox_api.netbox_connect import api_object


def upload_devices_to_netbox(url: str, token: str, file_path: str, **kwargs):
    """
    This function does the following:
    Create a Pynetbox Api Object with the users credentials.
    Reads the file data into a list of Device dataclasses.
    Validates the Device names and device types against Netbox.
    Converts the data in the Devices to their Netbox ID's.
    Changes those Device dataclasses into dictionaries.
    Creates the Devices in Netbox.
    :param url: The Netbox URL.
    :param token: The user's Netbox api token.
    :param file_path: The file path.
    """
    api = api_object(url, token)
    device_list = ReadData().read(file_path, **kwargs)
    ValidateData().validate_data(device_list, api, **{"fields": ["name", "device_type"]})
    queried_devices = QueryDevice(api).query_list(device_list)
    dictionary_devices = [asdict(device) for device in queried_devices]
    NetboxCreate(api).create_device(dictionary_devices)
    sys.stdout.write("Devices added to Netbox.\n")
