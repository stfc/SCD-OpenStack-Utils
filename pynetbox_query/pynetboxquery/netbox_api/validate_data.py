import sys
from typing import List
from pynetbox import api
from pynetboxquery.utils.device_dataclass import Device
from pynetboxquery.netbox_api.validate_methods import _ValidateMethods


# Disabling this Pylint warning as it is unnecessary.
# pylint: disable = R0903
class ValidateData(_ValidateMethods):
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
                sys.stdout.write(f"{result}\n")

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
