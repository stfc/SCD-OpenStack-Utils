from typing import Optional, Union, Dict, List


class NetboxDCIM:
    """
    This class contains methods that will interact create objects in Netbox.
    """

    def __init__(self, netbox):
        self.netbox = netbox

    def create_device(self, data: Union[Dict, List]) -> bool:
        """
        This method uses the pynetbox Api to create a device in Netbox.
        :param data: A list of or a single dictionary.
        :return: Returns bool.
        """
        devices = self.netbox.dcim.devices.create(data)
        return bool(devices)

    def create_device_type(
        self, model: str, slug: str, manufacturer: str, u_height: int = 1
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
