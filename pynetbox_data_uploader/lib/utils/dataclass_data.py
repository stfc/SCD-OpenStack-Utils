from dataclasses import dataclass


@dataclass
class Device:
    TENANT: str
    DEVICE_ROLE: str
    MANUFACTURER: str
    DEVICE_TYPE: str
    STATUS: str
    SITE: str
    LOCATION: str
    RACK: str
    FACE: str
    AIRFLOW: str
    POSITION: str
    NAME: str
    SERIAL: str
