from netbox_api import CsvUtils
from netbox_api import NetboxDCIM
from netbox_api import FormatDict
from pprint import pprint

url = "https://netbox-dev.esc.rl.ac.uk/"
token = "97f5987ed6c0ffd37dc1ddadc32957c4b224307f"
netbox_class = NetboxDCIM(url=url, token=token)
csv_file = r"DataFiles/xlsx_files/rack_883-884_hv-lenovo-2022_netboxload_2023-08-10/rack_883-884_hv-lenovo-2022_netboxload_2023-08-10_sheet_2.csv"

class_obj = CsvUtils()  # csv_things -> Python
dicts = class_obj.separate_data(class_obj.csv_to_python(csv_file))
pprint(dicts)
format_class = FormatDict(url=url, token=token, dicts=dicts)  # Python -> Format
dicts = format_class.iterate_dicts()
pprint(dicts)
