from Netbox_Api.netbox_connect import NetboxConnect
from typing import Optional


class NetboxExistence(NetboxConnect):
    """
    This class will check if certain objects such as device and device type exist in Netbox.
    """

    def __init__(self, url: str, token: str, api: Optional = None):
        if not api:
            self.netbox = NetboxConnect(url, token).api_object()
        else:
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
