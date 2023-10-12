from operator import attrgetter
from typing import Optional
from netbox_api.netbox_connect import NetboxConnect
from enums.dcim_device_id import DeviceInfoID
from enums.dcim_device_no_id import DeviceInfoNoID
# pylint:disable = too-few-public-methods


class NetboxGetID(NetboxConnect):
    """
    This class retrieves field value ID's from Netbox.
    """
    def __init__(self, url: str, token: str, api: Optional = None):
        """
        This method initialises the class with the following parameters.
        Also, it allows dependency injection testing.
        :param url: Netbox website URL.
        :param token: Netbox authentication token.
        """
        if not api:
            self.netbox = NetboxConnect(url, token).api_object()
        else:
            self.netbox = api
        self.enums_id = DeviceInfoID
        self.enums_no_id = DeviceInfoNoID

    def get_id(self, attr_string: str, netbox_value: str, site_value: str) -> int | str:
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
