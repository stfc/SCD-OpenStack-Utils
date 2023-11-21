from pathlib import Path
from csv import DictReader
from pandas import read_excel
from typing import List, Dict
from pynetboxquery.utils.device_dataclass import Device
from pynetboxquery.utils.error_classes import FileTypeNotSupported, DelimiterNotSpecifiedError, \
    SheetNameNotSpecifiedError


class ReadFile:

    def read_file(self, file_path, **kwargs):
        file_type = file_path.split(".")[-1]
        match file_type:
            case "csv":
                dictionary_list = ReadCSV(file_path).read()
            case "txt":
                dictionary_list = ReadTXT(file_path, **kwargs).read()
            case "xlsx":
                dictionary_list = ReadXLSX(file_path, **kwargs).read()
            case _:
                raise FileTypeNotSupported(
                    f"The file type '.{file_type}' is not supported by the method."
                )
        device_list = self._dict_to_dataclass(dictionary_list)
        return device_list

    @staticmethod
    def _check_file_path(file_path: str):
        """
        This method checks if the file path exists in the user's system.
        A FileNotFoundError will be raised if the file path is invalid.
        If the file path is valid nothing will happen.
        We don't need to declare that the file path is valid.
        :param file_path: The file path to the file
        """
        file_path_valid = Path(file_path).exists()
        if not file_path_valid:
            raise FileNotFoundError

    @staticmethod
    def _dict_to_dataclass(dictionary_list: List[Dict]) -> List[Device]:
        """
        This method takes a list of dictionaries and converts them all into Device dataclasses
        then returns the list.
        :param dictionary_list: A list of dictionaries.
        :return: A list of Device dataclasses.
        """
        return [Device(**dictionary) for dictionary in dictionary_list]


class ReadCSV(ReadFile):

    def __init__(self, file_path):
        self.file_path = file_path
        self._check_file_path(self.file_path)

    def read(self):
        """
        This method reads the contents of the csv file then returns a list of dictionaries
        where each dictionary is a row of data with the keys being the column headers.
        :return: A list of dictionaries.
        """
        with open(self.file_path, mode="r", encoding="UTF-8") as file:
            csv_reader = DictReader(file)
            dictionary_list = list(csv_reader)
        return dictionary_list


class ReadTXT(ReadFile):

    def __init__(self, file_path, **kwargs):
        self.file_path = file_path
        self._validate(kwargs)
        self.delimiter = kwargs["delimiter"]
        self._check_file_path(self.file_path)

    @staticmethod
    def _validate(kwargs):
        if "delimiter" not in kwargs:
            raise DelimiterNotSpecifiedError(
                "You must specify the delimiter in the text file."
            )

    def read(self):
        """
            This method reads the contents of the text file then returns a list of dictionaries
            where each dictionary is a row of data with the keys being the column headers.
            :return: A list of dictionaries.
            """
        with open(self.file_path, mode="r", encoding="UTF-8") as file:
            file_reader = DictReader(file, delimiter=self.delimiter)
            dictionary_list = list(file_reader)
        return dictionary_list


class ReadXLSX(ReadFile):

    def __init__(self, file_path, **kwargs):
        self.file_path = file_path
        self._validate(kwargs)
        self.sheet_name = kwargs["sheet_name"]
        self._check_file_path(self.file_path)

    @staticmethod
    def _validate(kwargs):
        if "sheet_name" not in kwargs:
            raise SheetNameNotSpecifiedError(
                "You must specify the sheet name in the excel workbook."
            )

    def read(self):
        """
        This method reads the contents of a Sheet in an Excel Workbook then returns a list of dictionaries
        where each dictionary is a row of data with the keys being the column headers.
        :return: A list of dictionaries.
        """
        dataframe = read_excel(self.file_path, sheet_name=self.sheet_name)
        dictionary_list = dataframe.to_dict(orient="records")
        return dictionary_list
