from typing import Union, Dict, List
from dataclasses import asdict
from pynetboxquery.utils.device_dataclass import Device


class NetboxCreate:
    """
    This class contains methods that will interact create objects in Netbox.
    """

    def __init__(self, api):
        """
        This initialises the class with the api object to be used by methods.
        """
        self.netbox = api

    def create_device(self, data: Union[Dict, List]) -> bool:
        """
        This method uses the pynetbox Api to create a device in Netbox.
        :param data: A list or a single dictionary containing data required to create devices in Netbox.
        :return: Returns bool if the devices where made or not.
        """
        devices = self.netbox.dcim.devices.create(data)
        return bool(devices)

    def create_device_type(self, data: Union[Dict, List]) -> bool:
        """
        This method creates a new device type in Netbox.
        :param data: A list or single dictionary containing data required to create device types in Netbox.
        :return: Returns bool if the device types where made or not.
        """
        device_type = self.netbox.dcim.device_types.create(data)
        return bool(device_type)
