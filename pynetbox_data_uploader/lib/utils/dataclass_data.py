from dataclasses import dataclass, fields


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
    face: str
    airflow: str
    position: str
    name: str
    serial: str

    def return_attrs(self):
        """
        This method returns a list of the names of the fields above.
        """

        return [field.name for field in list(fields(self))]
