from typing import List, Dict
from csv import DictReader
from pandas import read_excel


class _ReadMethods:
    """
    This class provides the read methods for different file types.
    All of which accept a file path and return a list of dictionaries.
    """
    @staticmethod
    def _read_csv(file_path: str) -> List[Dict]:
        """
        This method reads the contents of the csv file then returns a list of dictionaries
        where each dictionary is a row of data with the keys being the column headers.
        :param file_path: The file path to the file.
        :return: A list of dictionaries.
        """
        with open(file_path, mode="r", encoding="UTF-8") as file:
            csv_reader = DictReader(file)
            dictionary_list = list(csv_reader)
        return dictionary_list

    @staticmethod
    def _read_delimited_txt(file_path: str, delimiter: str) -> List[Dict]:
        """
        This method reads the contents of the text file then returns a list of dictionaries
        where each dictionary is a row of data with the keys being the column headers.
        :param file_path: The file path to the file.
        :return: A list of dictionaries.
        """
        with open(file_path, mode="r", encoding="UTF-8") as file:
            file_reader = DictReader(file, delimiter=delimiter)
            dictionary_list = list(file_reader)
        return dictionary_list

    @staticmethod
    def _read_xlsx(file_path: str, sheet_name: str) -> List[Dict]:
        """
        This method reads the contents of a Sheet in an Excel Workbook then returns a list of dictionaries
        where each dictionary is a row of data with the keys being the column headers.
        :param file_path: The file path to the file.
        :param sheet_name: The name of the sheet to read from.
        :return: A list of dictionaries.
        """
        dataframe = read_excel(file_path, sheet_name=sheet_name)
        dictionary_list = dataframe.to_dict(orient="records")
        return dictionary_list
