import csv
from typing import List, Dict
from pynetboxquery.utils.device_dataclass import Device


def open_file(file_path: str) -> List[Dict]:
    """
    This function opens the specified csv file and returns the DictReader class on it.
    :param file_path: The file path to the csv file.
    :return: Returns an instance of the DictReader Class.
    """
    with open(file_path, encoding="UTF-8") as file:
        csv_reader_obj = csv.DictReader(file)
        return list(csv_reader_obj)


def separate_data(csv_dicts: List[Dict]) -> List[Device]:
    """
    This method separates the data from the iterator object into a list of dataclasses for each device.
    :param csv_dicts: A list of dictionaries with each row of csv data.
    :return: Returns a list of dataclass objects.
    """
    devices = []
    for dictionary in csv_dicts:
        device = Device(**dictionary)
        devices.append(device)
    return devices


def read_csv(file_path: str) -> List[Device]:
    """
    This method calls the csv_to_python and separate_data method.
    This will take the csv file and return a list of device dataclasses
    :param file_path: The file path to the csv file to be read.
    :return: Returns a list of device dataclasses
    """
    return separate_data(open_file(file_path))
