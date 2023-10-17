from lib.netbox_api.netbox_create import NetboxCreate
from lib.netbox_api.netbox_connect import NetboxConnect
from lib.netbox_api.netbox_check import NetboxCheck
from lib.utils.csv_to_dict import FormatDict
from typing import List
import argparse


class CsvToNetbox:
    def __init__(self, url: str, token: str, file_path: str):
        self.netbox = NetboxConnect(url, token).api_object()
        self.file_path = file_path
        self.format_dict = FormatDict(api=self.netbox)
        self.exist = NetboxCheck(api=self.netbox)
        self.create = NetboxCreate(api=self.netbox)

    def read_csv(self) -> List:
        device_data = self.format_dict.csv_to_python(self.file_path)
        device_list = self.format_dict.separate_data(device_data)
        return device_list

    def check_netbox(self, device_list: List) -> bool:
        for device in device_list:
            device_exist = self.exist.check_device_exists(device["name"])
            if device_exist:
                raise Exception(f'Device {device["name"]} already exists in Netbox.')
            type_exist = self.exist.check_device_type_exists(device["device_type"])
            if not type_exist:
                raise Exception(f'Type {device["device_type"]} does not exist.')
        return True

    def convert_data(self, device_list: List) -> List:
        formatted_list = self.format_dict.iterate_dicts(device_list)
        return formatted_list

    def send_data(self, device_list: List) -> bool:
        devices = self.create.create_device(device_list)
        return bool(devices)


def arg_parser():
    parser = argparse.ArgumentParser(
        description="Create devices in Netbox from CSV files.",
        usage="python csv_to_netbox.py url token file_path"
    )
    parser.add_argument("url", help="The Netbox URL.")
    parser.add_argument("token", help="Your Netbox Token.")
    parser.add_argument("file_path", help="Your file path to csv files.")
    return parser.parse_args()
    
    
def do_csv_to_netbox(args):
    class_object = CsvToNetbox(url=args.url, token=args.token, file_path=args.file_path)
    device_list = class_object.read_csv()
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
