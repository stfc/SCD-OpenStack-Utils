from lib.netbox_api.netbox_create import NetboxCreate
from lib.netbox_api.netbox_connect import NetboxConnect
from lib.netbox_api.netbox_check import NetboxCheck
from lib.utils.csv_to_dict import FormatDict
import argparse

parser = argparse.ArgumentParser(
    description="Create devices in Netbox from CSV files.",
    usage="python csv_to_netbox.py url token file_path",
)
parser.add_argument("url", help="The Netbox URL.")
parser.add_argument("token", help="Your Netbox Token.")
parser.add_argument("file_path", help="Your file path to csv files.")
args = parser.parse_args()

netbox = NetboxConnect(url=args.url, token=args.token).api_object()
device_data = FormatDict(netbox).csv_to_python(args.file_path)
device_list = FormatDict(netbox).separate_data(device_data)
exist = NetboxCheck(netbox)
for device in device_list:
    device_exist = exist.check_device_exists(device["name"])
    if device_exist:
        raise Exception(f'Device {device["name"]} already exists in Netbox.')
    type_exist = exist.check_device_type_exists(device["device_type"])
    if not type_exist:
        raise Exception(f'Type {device["device_type"]} does not exist.')

formatted_list = FormatDict(netbox).iterate_dicts(device_list)
creation = NetboxCreate(netbox)
res = creation.create_device(formatted_list)
print(f'Device created: {res}')
print("No Errors?")


class CsvToDict(NetboxConnect):
    def __init__(self, url: str, token: str, file_path: str):
        self.netbox = super(url, token).api_object()
        self.file_path = file_path

    def read(self):
        pass

    def parse(self):
        pass

    def check(self):
        pass

    def convert(self):
        pass

    def send(self):
        pass


