from typing import Dict, List
from pandas import read_csv
from lib.netbox_api.netbox_get_id import NetboxGetID


class FormatDict:
    """
    This class takes dictionaries with string values and changes those to ID values from Netbox.
    """

    def __init__(self, api):
        """
        This method initialises the class with the following parameters.
        :param api: The Netbox object to pass into NetboxGetID
        """
        self.netbox = api

    def iterate_dicts(self, dicts: list) -> List:
        """
        This method iterates through each dictionary and calls a format method on each.
        :param dicts: A list of dictionaries to be formatted.
        :return: Returns the formatted dictionaries.
        """
        new_dicts = []
        for dictionary in dicts:
            new_dicts.append(self.format_dict(dictionary))
        return new_dicts

    def format_dict(self, dictionary) -> Dict:
        """
        This method iterates through each value in the dictionary.
        If the value needs to be converted into a Pynetbox ID it calls the .get() method.
        :param dictionary: The dictionary to be formatted
        :return: Returns the formatted dictionary
        """
        for key in dictionary:
            netbox_id = NetboxGetID(self.netbox).get_id_from_key(
                key=key, dictionary=dictionary
            )
            dictionary[key] = netbox_id
        return dictionary

    @staticmethod
    def csv_to_python(file_path: str) -> Dict:
        """
        This method reads data from csv files and writes them to a dictionary.
        :param file_path: The file path of the utils file to be read from.
        :return: Returns the data from the csv as a dictionary.
        """
        dataframe = read_csv(file_path)
        return dataframe.to_dict(orient="list")

    @staticmethod
    def separate_data(data: dict) -> List:
        """
        This method reduces Pandas utils to Dict conversion to individual dictionaries.
        :param data: The data from the utils file.
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
