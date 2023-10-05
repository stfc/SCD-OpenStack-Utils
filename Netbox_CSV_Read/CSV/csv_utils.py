import pandas as pd


class CsvUtils:
    """
    This class provides methods to read data from CSV files and allow the data to be easily read and used elsewhere.
    """
    @staticmethod
    def csv_to_python(file_path: str) -> dict:
        """
        This method reads data from csv files and writes them to a dictionary.
        :param file_path: The file path of the CSV file to be read from.
        :return: Returns the data from the csv as a dictionary.
        """
        with pd.read_csv(file_path) as dataframe:
            dataframe = dataframe.to_dict(orient="list")
        return dataframe

    @staticmethod
    def separate_data(data: dict) -> list:
        """
        This method reduces Pandas CSV to Dict conversion to individual dictionaries.
        :param data: The data from the CSV file
        :return: Returns a list of dictionaries which each represent a row of data from CSV.
        """
        data_keys = list(data.keys())
        len_rows = len(data[data_keys[0]]) - 1
        dicts = []
        for index in range(len_rows):
            new_dict = {}
            for key in data_keys:
                new_dict.update({key: data[key][index]})
            dicts.append(new_dict)
        return dicts
