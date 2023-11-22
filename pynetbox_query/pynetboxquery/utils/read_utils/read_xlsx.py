from typing import List
from pandas import read_excel
from pynetboxquery.utils.device_dataclass import Device
from pynetboxquery.utils.error_classes import SheetNameNotSpecifiedError
from pynetboxquery.utils.read_utils.read_abc import ReadAbstractBase


# Disabling this pylint warning as it is not necessary.
# pylint: disable = R0903
class ReadXLSX(ReadAbstractBase):
    """
    This class contains methods to read data from XLSX files into a list of Device dataclasses.
    """

    def __init__(self, file_path, **kwargs):
        super().__init__(file_path, **kwargs)
        self.sheet_name = kwargs["sheet_name"]

    @staticmethod
    def _validate(kwargs):
        """
        This method checks that the delimiter kwarg has been parsed.
        If not raise an error.
        """
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
