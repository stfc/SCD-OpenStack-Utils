from enum import Enum


class DeviceInfoID(Enum):
    DEVICE_ROLE = "dcim.device_roles"
    DESCRIPTION = "dcim.devices"
    DEVICE_TYPE = "dcim.device_types"
    RACK = "dcim.racks"
    LOCATION = "dcim.locations"
    TENANT = "tenancy.tenants"
    SITE = "dcim.sites"
    MANUFACTURER = "dcim.manufacturers"
