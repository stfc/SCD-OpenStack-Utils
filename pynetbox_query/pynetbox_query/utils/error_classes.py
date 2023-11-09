from pynetbox_query.utils.device_dataclass import Device


class DeviceFoundError(Exception):
    """
    This class is a custom exception for when a device is found to exist in Netbox.
    """

    def __init__(self, device: Device):
        self.message = f"The device, {device.name}, already exists in Netbox."
        super().__init__(self.message)


class DeviceTypeNotFoundError(Exception):
    """
    This class is a custom expectation for when a device type is found to not exist in Netbox.
    """

    def __init__(self, device: Device):
        self.message = (
            f"The device type, {device.device_type}, does not exist in Netbox.\n"
            f"This device type needs to be created in Netbox before the device can be created."
        )
        super().__init__(self.message)
