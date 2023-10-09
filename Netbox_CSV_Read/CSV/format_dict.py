from typing import Optional
from Enums.dcim_device_id import DeviceInfoID
from Enums.dcim_device_no_id import DeviceInfoNoID
from Netbox_Api.netbox_connect import NetboxConnect
from operator import attrgetter


class FormatDict(NetboxConnect):
    """
    This class takes dictionaries with string values and changes those to ID values from Netbox.
    """
    def __init__(self, url: str, token: str, dicts: list, api: Optional = None):
        """
        This method initialises the class with the following parameters.
        Also, it allows dependency injection testing.
        :param url: Netbox website URL.
        :param token: Netbox authentication token.
        :param dicts: A list of dictionaries to format.
        """
        if not api:
            self.netbox = NetboxConnect(url, token).api_object()
        else:
            self.netbox = api
        self.dicts = dicts
        self.enums_id = DeviceInfoID
        self.enums_no_id = DeviceInfoNoID

    def iterate_dicts(self) -> list:
        """
        This method iterates through each dictionary and calls a format method on each.
        :return: Returns the formatted dictionaries.
        """
        new_dicts = []
        for dictionary in self.dicts:
            new_dicts.append(self.format_dict(dictionary))
        return new_dicts

    def format_dict(self, dictionary) -> dict:
        """
        This method iterates through each value in the dictionary.
        If the value needs to be converted into a Pynetbox ID it calls the .get() method.
        :param dictionary: The dictionary to be formatted
        :return: Returns the formatted dictionary
        """
        for key in dictionary:
            if key not in list(self.enums_no_id.__members__):
                value = self.get_id(key, dictionary[key], dictionary["site"])
                dictionary[key] = value
        return dictionary

    def get_id(self, attr_string: str, netbox_value: str, site_value: str) -> id:
        """
        This method uses the Pynetbox Api .get() method to retrieve the ID of a string value from Netbox.
        :param attr_string: The attribute string to get.
        :param netbox_value: The value to search for in Netbox.
        :param site_value: The value of the site key in the dictionary
        :return: Returns the value/ID
        """
        attr_string = attr_string.upper()
        attr_to_look_for = getattr(self.enums_id, attr_string).value  # Gets Enums value
        value = attrgetter(attr_to_look_for)(self.netbox)  # Gets netbox attr
        if attr_string == "DEVICE_TYPE":
            value = value.get(slug=netbox_value).id
        elif attr_string == "LOCATION":
            if type(site_value) == int:
                site_name = self.netbox.dcim.sites.get(site_value).name
                site_slug = site_name.replace(" ", "-").lower()
            value = value.get(name=netbox_value, site=site_slug)
        else:
            value = value.get(name=netbox_value).id
        return value
