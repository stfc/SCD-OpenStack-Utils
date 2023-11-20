from typing import List
from pynetbox import api


# Disabling this Pylint warning, there are too few public methods.
# pylint: disable = R0903
class _ValidateMethods:
    @staticmethod
    def _check_device_name_in_netbox(device_name: str, netbox_api: api) -> bool:
        """
        This method will check if a device exists in Netbox.
        :param device_name: The name of the device.
        :return: Returns bool.
        """
        device = netbox_api.dcim.devices.get(name=device_name)
        return bool(device)

    def _check_list_device_name_in_netbox(
        self, device_names: List[str], netbox_api: api
    ) -> List[str]:
        """
        This method will call the validate method on each device name in the list and return the results.
        :param device_names: List of device names to check.
        :return: Results of the check.
        """
        results = []
        for name in device_names:
            in_netbox = self._check_device_name_in_netbox(name, netbox_api)
            results += [f"Device {name} exists in Netbox: {in_netbox}."]
        return results

    @staticmethod
    def _check_device_type_in_netbox(device_type: str, netbox_api: api) -> bool:
        """
        This method will check if a device type exists in Netbox.
        :param device_type: The device type.
        :return: Returns bool.
        """
        device_type = netbox_api.dcim.device_types.get(slug=device_type)
        return bool(device_type)

    def _check_list_device_type_in_netbox(
        self, device_type_list: List[str], netbox_api: api
    ) -> List[str]:
        """
        This method will call the validate method on each device type in the list and return the results.
        :param device_names: List of device types to check.
        :return: Results of the check.
        """
        results = []
        for device_type in device_type_list:
            in_netbox = self._check_device_type_in_netbox(device_type, netbox_api)
            results += [f"Device type {device_type} exists in Netbox: {in_netbox}."]
        return results
