import pandas as pd


class CSVtoDict:
    def __init__(self, file_path):
        self.file_path = file_path

    def csv_to_dicts(self):
        """
        This method organises data from CSV files into dictionaries for each row of data
        :return: Returns a list of dictionaries
        """
        dataframe = pd.read_csv(self.file_path)
        dataframe = dataframe.to_dict(orient="list")
        dataframe_keys = list(dataframe.keys())
        len_rows = len(dataframe[dataframe_keys[0]]) - 1
        dicts = []
        for index in range(len_rows):
            temp_dict = {}
            for key in dataframe_keys:
                temp_dict.update({key: f"{dataframe[key][index]}"})
            dicts.append(temp_dict)

        return dicts
