from typing import Optional
from netbox_connect import NetboxConnect


class NetboxDCIM:
    """
    This class contains methods that will interact with the Netbox Api.
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

    def create_device(self, data: dict | list) -> bool:
        """
        This method uses the pynetbox Api to create a device in Netbox.
        :param data: A list of or a single dictionary.
        :return: Returns bool.
        """
        devices = self.netbox.dcim.devices.create(data)
        return bool(devices)

    def create_device_type(
            self, model: str, slug: str, manufacturer: str, u_height=1
    ) -> bool:
        """
        This method creates a new device type in Netbox.
        :param model: The model name of the device.
        :param slug: The URL friendly version of the model name.
        :param manufacturer: The manufacturer of the device.
        :param u_height: This it the height of the device in the rack. Default 1.
        :return: Returns bool.
        """
        device_type = self.netbox.dcim.device_types.create(
            model=model, slug=slug, manufacturer=manufacturer, u_height=u_height
        )
        return bool(device_type)
