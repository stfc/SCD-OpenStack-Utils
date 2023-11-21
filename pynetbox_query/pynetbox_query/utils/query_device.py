from typing import List
from dataclasses import replace
from pynetbox_query.utils.device_dataclass import Device
from pynetbox_query.netbox_api.netbox_get_id import NetboxGetId


class QueryDevice:
    """
    This class contains methods that update the device dataclasses with ID's from Netbox.
    """

    def __init__(self, api):
        self.netbox = api

    def query_list(self, device_list: List[Device]) -> List[Device]:
        """
        This method iterates through the list of Devices.
        :param device_list: List of device dataclasses
        :return: Returns an updated list of device dataclasses.
        """
        new_device_list = []
        for device in device_list:
            new_device = self.query_device(device)
            new_device_list.append(new_device)
        return new_device_list

    def query_device(self, device: Device) -> Device:
        """
        This method calls the query method on each attribute of the device.
        :param device: The device to get the values from.
        :return: Returns the updated device.
        """
        changes = {}
        for attr in device.return_attrs():
            changes[attr] = NetboxGetId(self.netbox).get_id(device, attr)
        new_device = replace(device, **changes)
        return new_device
