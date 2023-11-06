import csv
from typing import List, Dict
from lib.utils.dataclass_data import Device


def open_file(file_path: str) -> List[Dict]:
    """
    This function opens the specified csv file and returns the DictReader class on it.
    :param file_path: The file path to the csv file.
    :return: Returns an instance of the DictReader Class.
    """
    with open(file_path, encoding="UTF-8") as file:
        csv_reader_obj = csv.DictReader(file)
        csv_dicts = [row for row in csv_reader_obj]
    return csv_dicts


def separate_data(csv_dicts: List[Dict]) -> List[Device]:
    """
    This method separates the data from the iterator object into a list of dataclasses for each device.
    :param csv_dicts: A list of dictionaries with each row of csv data.
    :return: Returns a list of dataclass objects.
    """
    devices = []
    for dictionary in csv_dicts:
        device = Device(
            tenant=dictionary["tenant"],
            device_role=dictionary["device_role"],
            manufacturer=dictionary["manufacturer"],
            device_type=dictionary["device_type"],
            status=dictionary["status"],
            site=dictionary["site"],
            location=dictionary["location"],
            rack=dictionary["rack"],
            face=dictionary["face"],
            airflow=dictionary["airflow"],
            position=dictionary["position"],
            name=dictionary["name"],
            serial=dictionary["serial"],
        )
        devices.append(device)
    return devices
