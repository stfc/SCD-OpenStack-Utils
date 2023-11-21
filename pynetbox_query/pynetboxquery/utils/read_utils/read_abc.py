from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict
from pynetboxquery.utils.device_dataclass import Device


# Disabling this pylint warning as it is not necessary.
# pylint: disable = R0903
class ReadAbstractBase(ABC):
    """
    This Abstract Base Class ensures any Read methods made contain at least all of this code.
    """

    def __init__(self, file_path, **kwargs):
        """
        Assigns the attribute file path. Checks the fie path is valid. Validates any kwargs needed.
        """
        self.file_path = file_path
        self._check_file_path(self.file_path)
        self._validate(kwargs)

    @abstractmethod
    def read(self) -> List[Dict]:
        """
        This method reads the contents of a file into a list od Device Dataclasses.
        """

    @staticmethod
    def _validate(kwargs):
        """
        This method checks if a certain argument is given in kwargs and if not raise an error.
        """

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
