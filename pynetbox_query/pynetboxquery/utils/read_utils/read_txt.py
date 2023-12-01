# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
from csv import DictReader
from typing import List
from pynetboxquery.utils.device_dataclass import Device
from pynetboxquery.utils.error_classes import DelimiterNotSpecifiedError
from pynetboxquery.utils.read_utils.read_abc import ReadAbstractBase


# Disabling this pylint warning as it is not necessary.
# pylint: disable = R0903
class ReadTXT(ReadAbstractBase):
    """
    This class contains methods to read data from TXT files into a list of Device dataclasses.
    """

    def __init__(self, file_path, **kwargs):
        super().__init__(file_path, **kwargs)
        self.delimiter = kwargs["delimiter"].replace("\\t", "\t")

    @staticmethod
    def _validate(kwargs):
        """
        This method checks that the delimiter kwarg has been parsed.
        If not raise an error.
        """
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
