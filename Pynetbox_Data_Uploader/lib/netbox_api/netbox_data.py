from operator import attrgetter
from typing import Optional, Union
from enums.dcim_device_id import DeviceInfoID
# pylint:disable = too-few-public-methods


class NetboxGetID:
    """
    This class retrieves field value ID's from Netbox.
    """

    def __init__(self, netbox: Optional = None):
        """
        This method allows the Netbox Api Object and Enums to be accessible within the class.
        """
        self.netbox = netbox
        self.enums_id = DeviceInfoID

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
        else:
            value = value.get(name=netbox_value).id
        return value
