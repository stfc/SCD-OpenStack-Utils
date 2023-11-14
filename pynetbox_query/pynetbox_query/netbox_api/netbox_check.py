from typing import List
from pynetbox_query.utils.error_classes import DeviceFoundError, DeviceTypeNotFoundError
from pynetbox_query.utils.device_dataclass import Device


class NetboxCheck:
    """
    This class contains methods that check if an object exists in Netbox.
    """

    def __init__(self, api):
        self.netbox = api

    def check_device_exists(self, device_name: str) -> bool:
        """
        This method will check if a device exists in Netbox.
        :param device_name: The name of the device.
        :return: Returns bool.
        """
        device = self.netbox.dcim.devices.get(name=device_name)
        return bool(device)

    def check_device_type_exists(self, device_type: str) -> bool:
        """
        This method will check if a device exists in Netbox.
        :param device_type: The name of the device.
        :return: Returns bool.
        """
        device_type = self.netbox.dcim.device_types.get(slug=device_type)
        return bool(device_type)

    def validate_devices(self, device_list: List[Device]) -> bool:
        """
        This method calls the check_device_exists and check_device_type_exists method on each device in the list.
        :param device_list: A list of devices.
        :return: Returns True if the devices don't exist. Raises a DeviceFoundError otherwise.
        """
        for device in device_list:
            device_exist = self.check_device_exists(device.name)
            if device_exist:
                raise DeviceFoundError(device)
        return True

    def validate_device_types(self, device_list: List[Device]) -> bool:
        """
        This method calls the check_device_exists and check_device_type_exists method on each device in the list.
        :param device_list: A list of devices.
        :return: Returns True if the device types do exist. Raises a DeviceTypeNotFound otherwise.
        """
        for device in device_list:
            type_exist = self.check_device_type_exists(device.device_type)
            if not type_exist:
                raise DeviceTypeNotFoundError(device)
        return True
