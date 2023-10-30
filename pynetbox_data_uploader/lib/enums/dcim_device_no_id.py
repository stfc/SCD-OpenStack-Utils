from enum import Enum


class DeviceInfoNoID(Enum):
    """
    This Enums Class stores enums that are used to retrieve data from Netbox.
    """

    POSITION = "position"
    NAME = "name"
    SERIAL = "serial"
    AIRFLOW = "airflow"
    STATUS = "status"
    FACE = "face"
