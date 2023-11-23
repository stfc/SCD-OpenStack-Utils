from csv import DictReader
from typing import List
from pynetboxquery.utils.device_dataclass import Device
from pynetboxquery.utils.read_utils.read_abc import ReadAbstractBase


# Disabling this pylint warning as it is not necessary.
# pylint: disable = R0903
class ReadCSV(ReadAbstractBase):
    """
    This class contains methods to read data from CSV files into a list of Device dataclasses.
    """

    def read(self) -> List[Device]:
        """
        This method reads the contents of the csv file then returns a list of dictionaries
        where each dictionary is a row of data with the keys being the column headers.
        :return: A list of dictionaries.
        """
        with open(self.file_path, mode="r", encoding="UTF-8") as file:
            csv_reader = DictReader(file)
            dictionary_list = list(csv_reader)
        device_list = self._dict_to_dataclass(dictionary_list)
        return device_list

    @staticmethod
    def _validate(self):
        pass
