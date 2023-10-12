from enum import Enum


class DeviceInfoNoID(Enum):
    """
    This Enums Class stores enums that are used to retrieve data from Netbox.
    """
    position = "position"
    name = "name"
    serial = "serial"
    airflow = "airflow"
    status = "status"
    face = "face"