from typing import List
import argparse
from lib.netbox_api.netbox_create import NetboxCreate
from lib.netbox_api.netbox_connect import NetboxConnect
from lib.netbox_api.netbox_check import NetboxCheck
from lib.utils.csv_to_dict import FormatDict

# pylint:disable = broad-exception-raised
# Disabled this pylint warning as the exception doesn't catch an error.
# We want it to stop the program if a device already exists in netbox.


class CsvToNetbox:
    """
    This class contains organised methods in the 4 step proccess of reading csv's to then uploading to Netbox.
    """
    def __init__(self, url: str, token: str):
        """
        This initialises the class with the following parameters.
        It also allows the rest of the class to access the imported Classes.
        :param url: The Netbox url.
        :param token: The Netbox auth token.
        """
        self.netbox = NetboxConnect(url, token).api_object()
        self.format_dict = FormatDict(api=self.netbox)
        self.exist = NetboxCheck(api=self.netbox)
        self.create = NetboxCreate(api=self.netbox)

    def read_csv(self, file_path) -> List:
        """
        This method calls the csv_to_python and seperate_data method.
        This will take the csv file and return a list of device dictionaries.
        :return: Returns a list of devices
        """
        device_data = self.format_dict.csv_to_python(file_path)
        device_list = self.format_dict.separate_data(device_data)
        return device_list

    def check_netbox(self, device_list: List) -> bool:
        """
        This method calls the check_device_exists and check_device_type_exists method on each device in the list.
        :param device_list: A list of devices.
        :return: Returns True if the devices don't exist and device types do exist. Raises an Exception otherwise.
        """
        for device in device_list:
            device_exist = self.exist.check_device_exists(device["name"])
            if device_exist:
                raise Exception(f'Device {device["name"]} already exists in Netbox.')
            type_exist = self.exist.check_device_type_exists(device["device_type"])
            if not type_exist:
                raise Exception(f'Type {device["device_type"]} does not exist.')
        return True

    def convert_data(self, device_list: List) -> List:
        """
        This method calls the iterate_dict method.
        :param device_list: A list of devices.
        :return: Returns the updated list of devices.
        """
        formatted_list = self.format_dict.iterate_dicts(device_list)
        return formatted_list

    def send_data(self, device_list: List) -> bool:
        """
        This method calls the device create method to create devices in Netbox.
        :param device_list: A list of devices.
        :return: Returns bool whether the devices where created.
        """
        devices = self.create.create_device(device_list)
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
    device_list = class_object.read_csv(args.file_path)
    class_object.check_netbox(device_list)
    format_list = class_object.convert_data(device_list)
    result = class_object.send_data(format_list)
    return result


if __name__ == "__main__":
    arguments = arg_parser()
    if do_csv_to_netbox(arguments):
        print("Done.")
    else:
        print("Uh Oh.")
