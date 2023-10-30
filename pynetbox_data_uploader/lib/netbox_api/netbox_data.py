from operator import attrgetter
from typing import Union, Dict
from lib.enums.dcim_device_id import DeviceInfoID
from lib.enums.dcim_device_no_id import DeviceInfoNoID

# pylint:disable = too-few-public-methods


class NetboxGetID:
    """
    This class retrieves field value ID's from Netbox.
    """

    def __init__(self, api):
        """
        This method allows the Netbox Api Object and Enums to be accessible within the class.
        """
        self.netbox = api
        self.enums_id = DeviceInfoID
        self.enums_no_id = DeviceInfoNoID

    def get_id(
        self, attr_string: str, netbox_value: str, site_value: str
    ) -> Union[int, str]:
        """
        This method uses Pynetbox Api .get() to retrieve the ID of a string value from Netbox.
        :param attr_string: The attribute string to get.
        :param netbox_value: The value to search for in Netbox.
        :param site_value: The value of the site key in the dictionary
        :return: Returns the value/ID
        """
        attr_string = attr_string.upper()
        attr_to_look_for = getattr(self.enums_id, attr_string).value  # Gets enums value
        value = attrgetter(attr_to_look_for)(self.netbox)  # Gets netbox attr
        if attr_string == "DEVICE_TYPE":
            value = value.get(slug=netbox_value).id
        elif attr_string == "LOCATION":
            if isinstance(site_value, int):
                site_name = self.netbox.dcim.sites.get(site_value).name
                site_slug = site_name.replace(" ", "-").lower()
                value = value.get(name=netbox_value, site=site_slug)
                list_value = list(value)
                list_value = [item for item in list_value if item[0] == "id"]
                value = list_value[0][1]
        else:
            value = value.get(name=netbox_value).id
        return value

    def get_id_from_key(self, key: str, dictionary: Dict) -> Union[str, int]:
        """
        This method calls the get_id method to retrieve the Netbox id of a value.
        :param key: The attribute to look for.
        :param dictionary: The device dictionary being referenced.
        :return: If an ID was needed and found it returns the ID. If an ID was not needed it returns the original value.
        """
        if key.upper() not in list(self.enums_no_id.__members__):
            value = self.get_id(
                attr_string=key,
                netbox_value=dictionary[key],
                site_value=dictionary["site"],
            )
            return value
        return dictionary[key]
