from dataclasses import dataclass
from typing import Optional


# pylint: disable = R0902
@dataclass
class Device:
    """
    This class instantiates device objects with the device data.
    """

    tenant: str
    device_role: str
    manufacturer: str
    device_type: str
    status: str
    site: str
    location: str
    rack: str
    position: str
    name: str
    serial: str
    face: Optional[str] = None
    airflow: Optional[str] = None
