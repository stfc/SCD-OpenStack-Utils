from enum import Enum


class DeviceInfoID(Enum):
    """
    This Enums Class stores enums that are used to retrieve data from Netbox.
    """

    DEVICE_ROLE = "dcim.device_roles"
    DESCRIPTION = "dcim.devices"
    DEVICE_TYPE = "dcim.device_types"
    RACK = "dcim.racks"
    LOCATION = "dcim.locations"
    TENANT = "tenancy.tenants"
    SITE = "dcim.sites"
    MANUFACTURER = "dcim.manufacturers"
