from typing import Optional


class NetboxCheck:
    """
    This class contains methods that check if an object exists in Netbox.
    """

    def __init__(self, netbox: Optional = None):
        self.netbox = netbox

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
