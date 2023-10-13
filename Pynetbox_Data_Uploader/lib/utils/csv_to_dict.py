from typing import List, Dict
import pandas as pd


class CsvUtils:
    """
    This class provides methods to read data from csv files
    and allow the data to be easily read and used elsewhere.
    """

    @staticmethod
    def csv_to_python(file_path: str) -> Dict:
        """
        This method reads data from csv files and writes them to a dictionary.
        :param file_path: The file path of the utils file to be read from.
        :return: Returns the data from the csv as a dictionary.
        """
        dataframe = pd.read_csv(file_path)
        dataframe = dataframe.to_dict(orient="list")
        return dataframe

    @staticmethod
    def separate_data(data: dict) -> List:
        """
        This method reduces Pandas utils to Dict conversion to individual dictionaries.
        :param data: The data from the utils file
        :return: Returns a list of dictionaries which each represent a row of data from utils.
        """
        data_keys = list(data.keys())
        len_rows = len(data[data_keys[0]])
        dicts = []
        for index in range(len_rows):
            new_dict = {}
            for key in data_keys:
                new_dict.update({key: data[key][index]})
            dicts.append(new_dict)
        return dicts
