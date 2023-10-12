from typing import Dict, List
from enums.dcim_device_id import DeviceInfoID
from enums.dcim_device_no_id import DeviceInfoNoID
from netbox_api.netbox_connect import NetboxConnect
from netbox_api.netbox_data import NetboxGetID


class FormatDict(NetboxConnect):
    """
    This class takes dictionaries with string values and changes those to ID values from Netbox.
    """
    def __init__(self, dicts: list):
        """
        This method initialises the class with the following parameters.
        Also, it allows dependency injection testing.
        :param dicts: A list of dictionaries to format.
        """
        self.dicts = dicts
        self.enums_id = DeviceInfoID
        self.enums_no_id = DeviceInfoNoID

    def iterate_dicts(self) -> List:
        """
        This method iterates through each dictionary and calls a format method on each.
        :return: Returns the formatted dictionaries.
        """
        new_dicts = []
        for dictionary in self.dicts:
            new_dicts.append(self.format_dict(dictionary))
        return new_dicts

    def format_dict(self, dictionary) -> Dict:
        """
        This method iterates through each value in the dictionary.
        If the value needs to be converted into a Pynetbox ID it calls the .get() method.
        :param dictionary: The dictionary to be formatted
        :return: Returns the formatted dictionary
        """
        for key in dictionary:
            if key not in list(self.enums_no_id.__members__):
                value = NetboxGetID.get_id(key, dictionary[key], dictionary["site"])
                dictionary[key] = value
        return dictionary
