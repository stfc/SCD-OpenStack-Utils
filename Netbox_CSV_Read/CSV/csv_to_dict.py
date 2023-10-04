import pandas as pd


class CSVtoDict:

    @staticmethod
    def csv_to_python(file_path: str) -> dict:
        """
        This method organises data from CSV files into dictionaries for each row of data.
        :param file_path: The file path of the CSV file to be read from.
        :return: Returns the data from the csv as a dictionary.
        """
        dataframe = pd.read_csv(file_path)
        dataframe = dataframe.to_dict(orient="list")
        return dataframe

    @staticmethod
    def separate_data(data: dict) -> list:
        """
        This method takes the data dictionary and separates each row into a single dictionary.
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
