from typing import List
from pynetbox import api
from pynetboxquery.utils.device_dataclass import Device


# Disabling this Pylint warning as it is unnecessary.
# pylint: disable = R0903
class ValidateData:
    """
    This class contains methods that check if things exist in Netbox or not.
    """

    def validate_data(
        self, device_list: List[Device], netbox_api: api, fields: List[str]
    ):
        """
        This method will take a list of dataclasses.
        Validate any data specified by the key word arguments.
        :param device_list: A list of Device dataclasses containing the data.
        :param netbox_api: The Api Object for Netbox.
        :param fields: The Device fields to check.
        """
        for field in fields:
            results = self._call_validation_methods(device_list, netbox_api, field)
            for result in results:
                print(f"{result}\n")

    def _call_validation_methods(
        self, device_list: List[Device], netbox_api: api, field: str
    ) -> List[str]:
        """
        This method will validate the field data by calling the correct validate method.
        :param device_list: List of devices to validate.
        :param netbox_api: The Api Object for Netbox.
        :param field: Field to validate.
        :return: Returns the results of the validation call.
        """
        match field:
            case "name":
                device_names = [device.name for device in device_list]
                results = self._check_list_device_name_in_netbox(
                    device_names, netbox_api
                )
            case "device_type":
                device_types = [device.device_type for device in device_list]
                results = self._check_list_device_type_in_netbox(
                    device_types, netbox_api
                )
            case _:
                results = [f"Could not find a field for the argument: {field}."]
        return results

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
        :param device_type_list: List of device types to check.
        :return: Results of the check.
        """
        results = []
        for device_type in device_type_list:
            in_netbox = self._check_device_type_in_netbox(device_type, netbox_api)
            results += [f"Device type {device_type} exists in Netbox: {in_netbox}."]
        return results
    