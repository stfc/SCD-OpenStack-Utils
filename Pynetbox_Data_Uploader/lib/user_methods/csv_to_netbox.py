from netbox_api.netbox_create import NetboxCreate
from netbox_api.netbox_connect import NetboxConnect
from netbox_api.netbox_check import NetboxCheck
from utils.csv_to_dict import FormatDict
import argparse

parser = argparse.ArgumentParser(
    description="Create devices in Netbox from CSV files.",
    usage="python csv_to_netbox.py url token file_path",
)
parser.add_argument("url", help="The Netbox URL.")
parser.add_argument("token", help="Your Netbox Token.")
parser.add_argument("file_path", help="Your file path to csv files.")
args = parser.parse_args()

netbox = NetboxConnect(url=args.url, token=args.token)
device_data = FormatDict(netbox).csv_to_python(args.file_path)
device_list = FormatDict(netbox).separate_data(device_data)
for device in device_list:
    exist = NetboxCheck(netbox).check_device_exists(device["device_name"])
    if exist:
        raise Exception(f'Device {device["device_name"]} already exists in Netbox.')
    else:
        pass

