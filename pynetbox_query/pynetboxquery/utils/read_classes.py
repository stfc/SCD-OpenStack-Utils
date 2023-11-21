from csv import DictReader
from pandas import read_excel
from typing import List
from pynetboxquery.utils.device_dataclass import Device
from pynetboxquery.utils.error_classes import FileTypeNotSupported, DelimiterNotSpecifiedError, \
    SheetNameNotSpecifiedError
from pynetboxquery.utils.read_abc import ReadAbstractBase


class ReadFile:

    @staticmethod
    def read_file(file_path, **kwargs) -> List[Device]:
        file_type = file_path.split(".")[-1]
        match file_type:
            case "csv":
                device_list = ReadCSV(file_path).read()
            case "txt":
                device_list = ReadTXT(file_path, **kwargs).read()
            case "xlsx":
                device_list = ReadXLSX(file_path, **kwargs).read()
            case _:
                raise FileTypeNotSupported(
                    f"The file type '.{file_type}' is not supported by the method."
                )
        return device_list


class ReadCSV(ReadAbstractBase):

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


class ReadTXT(ReadAbstractBase):

    def __init__(self, file_path, **kwargs):
        super().__init__(file_path, **kwargs)
        self.delimiter = kwargs["delimiter"]

    @staticmethod
    def _validate(kwargs):
        if "delimiter" not in kwargs:
            raise DelimiterNotSpecifiedError(
                "You must specify the delimiter in the text file."
            )

    def read(self) -> List[Device]:
        """
            This method reads the contents of the text file then returns a list of dictionaries
            where each dictionary is a row of data with the keys being the column headers.
            :return: A list of dictionaries.
            """
        with open(self.file_path, mode="r", encoding="UTF-8") as file:
            file_reader = DictReader(file, delimiter=self.delimiter)
            dictionary_list = list(file_reader)
        device_list = self._dict_to_dataclass(dictionary_list)
        return device_list


class ReadXLSX(ReadAbstractBase):

    def __init__(self, file_path, **kwargs):
        super().__init__(file_path, **kwargs)
        self.sheet_name = kwargs["sheet_name"]

    @staticmethod
    def _validate(kwargs):
        if "sheet_name" not in kwargs:
            raise SheetNameNotSpecifiedError(
                "You must specify the sheet name in the excel workbook."
            )

    def read(self) -> List[Device]:
        """
        This method reads the contents of a Sheet in an Excel Workbook then returns a list of dictionaries
        where each dictionary is a row of data with the keys being the column headers.
        :return: A list of dictionaries.
        """
        dataframe = read_excel(self.file_path, sheet_name=self.sheet_name)
        dictionary_list = dataframe.to_dict(orient="records")
        device_list = self._dict_to_dataclass(dictionary_list)
        return device_list
