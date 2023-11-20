from pathlib import Path
from typing import List, Dict
from pynetboxquery.utils.error_classes import *
from pynetboxquery.utils.device_dataclass import Device
from pynetboxquery.utils.read_methods import _ReadMethods


class ReadData(_ReadMethods):
    """
    This class contains methods to read data from different file types into a list of dictionaries.
    Only the "read" method should be called by the user as it can differentiate between different file types.
    The rest of the methods read data from the file into a list of dictionaries.
    """

    def read(self, file_path: str, **kwargs) -> List[Device]:
        """
        This method will:
        Check the file path is valid.
        Call the appropriate read method depending on the file type returning a list of dictionaries.
        Convert that list of dictionaries to a list of Device dataclasses.
        Return a list of device dataclasses for the data in the file.
        :param file_path: The file path to the file.
        :param kwargs: delimiter -> text file separator | sheet_name -> Excel Workbook sheet name.
        :return: Returns the list of Device dataclasses.
        """

        file_type = file_path.split(".")[-1]
        self._check_file_path(file_path)
        self._validate_kwargs(file_type, **kwargs)
        match file_type:
            case "csv":
                dictionary_list = self._read_csv(file_path)
            case "txt":
                dictionary_list = self._read_delimited_txt(file_path, kwargs["delimiter"])
            case "xlsx":
                dictionary_list = self._read_xlsx(file_path, kwargs["sheet_name"])
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
    def _validate_kwargs(file_type: str, **kwargs):
        """
        This method validates that the correct arguments are parsed for each file type method.
        An error will be raised if the arguments are missing.
        The code will continue with no response if the arguments are valid.
        :param file_type: The file type tells us what arguments to check for.
        :param kwargs: The key word arguments being parsed
        """
        match file_type:
            case "txt":
                if "delimiter" not in kwargs:
                    raise DelimiterNotSpecifiedError(
                        r"You have not specified a delimiter for the text file. e.g. ',' or '\t'."
                    )
            case "xlsx":
                if "sheet_name" not in kwargs:
                    raise SheetNameNotSpecifiedError(
                        r"You have not specified a sheet name for the workbook. e.g. 'Sheet1'."
                    )
            case _:
                pass

    @staticmethod
    def _dict_to_dataclass(dictionary_list: List[Dict]) -> List[Device]:
        """
        This method takes a list of dictionaries and converts them all into Device dataclasses
        then returns the list.
        :param dictionary_list: A list of dictionaries.
        :return: A list of Device dataclasses.
        """
        return [Device(**dictionary) for dictionary in dictionary_list]
