from csv import reader
from typing import List
from pynetbox_data_uploader.lib.utils.dataclass_data import Device


def separate_data(file_path: str) -> List[Device]:
    """
    This method separates the data from the iterator object into a list of dataclasses for each device.
    :param file_path: The file path to the csv file.
    :return: Returns a list of dataclass objects.
    """
    with open(file_path) as file:
        csv_reader_obj = reader(file)
        column_headers = next(csv_reader_obj)
        devices = []
        for row in csv_reader_obj:
            device = Device(
                TENANT=row[column_headers.index('tenant')],
                DEVICE_ROLE=row[column_headers.index('device_role')],
                MANUFACTURER=row[column_headers.index('manufacturer')],
                DEVICE_TYPE=row[column_headers.index('device_type')],
                STATUS=row[column_headers.index('status')],
                SITE=row[column_headers.index('site')],
                LOCATION=row[column_headers.index('location')],
                RACK=row[column_headers.index('rack')],
                FACE=row[column_headers.index('face')],
                AIRFLOW=row[column_headers.index('airflow')],
                POSITION=row[column_headers.index('position')],
                NAME=row[column_headers.index('name')],
                SERIAL=row[column_headers.index('serial')])
            devices.append(device)
    return devices
