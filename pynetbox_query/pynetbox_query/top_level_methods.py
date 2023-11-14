from typing import List, Dict
from pathlib import Path
from dataclasses import asdict
from pynetbox_query.netbox_api.netbox_create import NetboxCreate
from pynetbox_query.netbox_api.netbox_connect import NetboxConnect
from pynetbox_query.netbox_api.netbox_check import NetboxCheck
from pynetbox_query.utils.csv_to_dataclass import open_file, separate_data
from pynetbox_query.utils.query_device import QueryDevice
from pynetbox_query.utils.device_dataclass import Device
from pynetbox_query.utils.error_classes import DeviceFoundError, DeviceTypeNotFoundError


class TopLevelMethods:
    """
    This class contains organised methods that can be used in user used script.
    """

    def __init__(self, url: str, token: str):
        """
        This initialises the class with the following parameters.
        It also allows the rest of the class to access the imported Classes.
        :param url: The Netbox url.
        :param token: The Netbox auth token.
        """
        self.netbox = NetboxConnect(url, token).api_object()
        self.exist = NetboxCheck(self.netbox)
        self.create = NetboxCreate(self.netbox)
        self.query_dataclass = QueryDevice(self.netbox)

    @staticmethod
    def check_file_path(file_path: str):
        """
        This method checks if the filepath is valid. Raises a FileNotFoundError if it's invalid.
        :param file_path: The path to the csv file.
        """
        valid = Path(file_path).exists()
        if not valid:
            raise FileNotFoundError(f"Filepath: {file_path} is not valid.")

    @staticmethod
    def read_csv(file_path: str) -> List[Device]:
        """
        This method calls the csv_to_python and separate_data method.
        This will take the csv file and return a list of device dataclasses
        :param file_path: The file path to the csv file to be read.
        :return: Returns a list of device dataclasses
        """
        return separate_data(open_file(file_path))

    @staticmethod
    def dataclass_to_dict(device_list: List[Device]) -> List[Dict]:
        """
        This method converts the list of Devices into a list of dictionaries for Netbox Create.
        :param device_list: A list of Device dataclasses.
        :return: Returns the list of Devices as dictionaries.
        """
        return [asdict(device) for device in device_list]

    def validate_devices(self, device_list: List[Device]) -> bool:
        """
        This method calls the check_device_exists and check_device_type_exists method on each device in the list.
        :param device_list: A list of devices.
        :return: Returns True if the devices don't exist. Raises a DeviceFoundError otherwise.
        """
        for device in device_list:
            device_exist = self.exist.check_device_exists(device.name)
            if device_exist:
                raise DeviceFoundError(device)
        return True

    def validate_device_types(self, device_list: List[Device]) -> bool:
        """
        This method calls the check_device_exists and check_device_type_exists method on each device in the list.
        :param device_list: A list of devices.
        :return: Returns True if the device types do exist. Raises a DeviceTypeNotFound otherwise.
        """
        for device in device_list:
            type_exist = self.exist.check_device_type_exists(device.device_type)
            if not type_exist:
                raise DeviceTypeNotFoundError(device)
        return True

    def check_device_exist(self, device: Device):
        device_exists = self.exist.check_device_exists(device.name)
        return device_exists

    def check_device_type_exists(self, device: Device):
        device_type_exists = self.exist.check_device_type_exists(device.device_type)
        return device_type_exists

    def query_data(self, device_list: List[Device]) -> List[Device]:
        """
        This method calls the iterate_dict method.
        :param device_list: A list of devices.
        :return: Returns the updated list of devices.
        """
        queried_list = self.query_dataclass.query_list(device_list)
        return queried_list

    def send_data(self, device_list: List[Device]) -> bool:
        """
        This method calls the device create method to create devices in Netbox.
        :param device_list: A list of devices.
        :return: Returns bool whether the devices where created.
        """
        dict_list = self.dataclass_to_dict(device_list)
        devices = self.create.create_device(dict_list)
        return bool(devices)