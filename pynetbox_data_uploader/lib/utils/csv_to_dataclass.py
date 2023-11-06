import csv
from typing import List
from lib.utils.dataclass_data import Device


def open_file(file_path: str) -> csv.DictReader:
    """
    This function opens the specified csv file and returns the DictReader class on it.
    :param file_path: The file path to the csv file.
    :return: Returns an instance of the DictReader Class.
    """
    with open(file_path, encoding="UTF-8") as file:
        csv_reader_obj = csv.DictReader(file)
    return csv_reader_obj


def separate_data(csv_reader_obj: csv.DictReader) -> List[Device]:
    """
    This method separates the data from the iterator object into a list of dataclasses for each device.
    :param csv_reader_obj: The DictReader class with the data.
    :return: Returns a list of dataclass objects.
    """
    devices = []
    for row in csv_reader_obj:
        device = Device(
            tenant=row["tenant"],
            device_role=row["device_role"],
            manufacturer=row["manufacturer"],
            device_type=row["device_type"],
            status=row["status"],
            site=row["site"],
            location=row["location"],
            rack=row["rack"],
            face=row["face"],
            airflow=row["airflow"],
            position=row["position"],
            name=row["name"],
            serial=row["serial"],
        )
        devices.append(device)
    return devices
