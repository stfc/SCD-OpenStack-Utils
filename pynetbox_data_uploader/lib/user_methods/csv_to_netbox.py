from typing import List, Dict
from pathlib import Path
from dataclasses import asdict
import argparse
import sys
from netbox_api.netbox_create import NetboxCreate
from netbox_api.netbox_connect import NetboxConnect
from netbox_api.netbox_check import NetboxCheck
from utils.csv_to_dataclass import open_file, separate_data
from utils.query_device import QueryDevice
from utils.device_dataclass import Device
from utils.error_classes import DeviceFoundError, DeviceTypeNotFoundError


class CsvToNetbox:
    """
    This class contains organised methods in the 4-step process of reading csv's to then uploading to Netbox.
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
        This method calls the csv_to_python and seperate_data method.
        This will take the csv file and return a list of device dictionaries.
        :param file_path: The file path to the csv file to be read.
        :return: Returns a list of devices
        """
        return separate_data(open_file(file_path))

    def check_netbox_device(self, device_list: List[Device]) -> bool:
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

    def check_netbox_device_type(self, device_list: List[Device]) -> bool:
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

    def convert_data(self, device_list: List[Device]) -> List[Device]:
        """
        This method calls the iterate_dict method.
        :param device_list: A list of devices.
        :return: Returns the updated list of devices.
        """
        queried_list = self.query_dataclass.query_list(device_list)
        return queried_list

    @staticmethod
    def dataclass_to_dict(device_list: List[Device]) -> List[Dict]:
        """
        This method converts the list of Devices into a list of dictionaries for Netbox Create.
        :param device_list: A list of Device dataclasses.
        :return: Returns the list of Devices as dictionaries.
        """
        return [asdict(device) for device in device_list]

    def send_data(self, device_list: List[Device]) -> bool:
        """
        This method calls the device create method to create devices in Netbox.
        :param device_list: A list of devices.
        :return: Returns bool whether the devices where created.
        """
        dict_list = self.dataclass_to_dict(device_list)
        devices = self.create.create_device(dict_list)
        return bool(devices)


def arg_parser():
    """
    This function creates a parser object and adds 3 arguments to it.
    This allows users to run the python file with arguments. Like a script.
    """
    parser = argparse.ArgumentParser(
        description="Create devices in Netbox from CSV files.",
        usage="python csv_to_netbox.py url token file_path",
    )
    parser.add_argument("url", help="The Netbox URL.")
    parser.add_argument("token", help="Your Netbox Token.")
    parser.add_argument("file_path", help="Your file path to csv files.")
    return parser.parse_args()


def do_csv_to_netbox(args) -> bool:
    """
    This function calls the methods from CsvToNetbox class.
    :param args: The arguments from argparse. Supplied when the user runs the file from CLI.
    :return: Returns bool if devices where created or not.
    """
    class_object = CsvToNetbox(url=args.url, token=args.token)
    class_object.check_file_path(args.file_path)
    device_list = class_object.read_csv(args.file_path)
    class_object.check_netbox_device(device_list)
    class_object.check_netbox_device_type(device_list)
    converted_device_list = class_object.convert_data(device_list)
    result = class_object.send_data(converted_device_list)
    return result


def main():
    """
    This function calls the necessary functions to call all other methods.
    """
    sys.stdout.write("Starting...")
    arguments = arg_parser()
    do_csv_to_netbox(arguments)
    sys.stdout.write("Finished.")


if __name__ == "__main__":
    main()
