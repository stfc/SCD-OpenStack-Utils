"""
This script will collect data from Prometheus and write it to a CSV file.
It will correctly format data from "openstack" and "node" queries.
It uses a time range to query over a period of time. The time is required to be in UNIX Epoch format.
You may need to play with the step in the RawData class as sometimes you will be querying at an
interval where there is no data.
If you are querying a large amount of data, you may need to increase the amount of RAM allocated to Python.
Pagination is not implemented, so it can be easy to run out of memory.
"""

from typing import List, Dict
from json import loads
from socket import gethostbyaddr
from datetime import datetime
from requests import get, Response


class RawData:
    """
    This class gets the raw JSON data from the Prometheus endpoint and writes that to files.
    """

    def __init__(self, metrics: List[str], start: str, end: str, url: str):
        self.metrics = metrics
        self.start = start
        self.end = end
        self.step = 7200
        self.endpoint = url

    def request_to_json_file(self):
        """
        This method runs the request and write function for each metric you want to query for.
        It will write into CSV files called the metrics name.
        """
        for metric in self.metrics:
            payload = {
                "query": metric,
                "start": self.start,
                "end": self.end,
                "step": self.step,
            }
            response = self.http_request(payload)
            self.write_json_file(metric, response)

    def http_request(self, metric) -> Response:
        """
        This method uses the request library's get function to send a HTTP GET request to the endpoint.
        :param metric: The metric to query for
        :return: The HTTP response
        """
        response = get(self.endpoint, params=metric, timeout=300)
        return response

    @staticmethod
    def write_json_file(name: str, response: Response):
        """
        This method writes the response data to a file.
        :param name: The metric name
        :param response: The HTTP response
        """
        with open(f"{name}.csv", "w", encoding="utf-8") as json_file:
            data = response.json()
            json_file.write(str(data))


class JsonToCSV:
    """
    This class trims the raw JSON data to a CSV format file.
    """

    def __init__(self, metrics: List[str]):
        self.metrics = metrics

    def json_to_csv(self):
        """
        This method reads a file and calls the format function for each file.
        Then writes the newly formatted data to that original file.
        """
        for metric in self.metrics:
            json_data = self.read_json(metric)
            dictionary = self.json_to_dict(json_data)
            self.dict_to_csv(dictionary)

    @staticmethod
    def read_json(file_name: str) -> str:
        """
        This method reads the data in to Python from the file.
        :param file_name: The file name to read
        :return: Returns the data read from the file
        """
        with open(f"{file_name}.csv", "r", encoding="utf-8") as json_file:
            json_data = json_file.read()
            return json_data

    @staticmethod
    def json_to_dict(data: str) -> Dict:
        """
        This method converts the read string into a Python dictionary.
        :param data: The data read from the file
        :return: Returns the data as a dictionary
        """
        data = data.replace("'", '"')
        json = loads(data)
        return json

    def dict_to_csv(self, json: Dict):
        """
        This method writes the data into a CSV file formatted using f strings to only write the data we want.
        :param json: The data from the file in a dictionary
        """
        data = json["data"]["result"]
        if data[0]["metric"]["__name__"].startswith("openstack"):
            self.dict_to_csv_openstack(data)
        elif data[0]["metric"]["__name__"].startswith("node"):
            self.dict_to_csv_node(data)
        else:
            raise Exception(
                "Unsupported query type: openstack or node currently supported."
            )

    @staticmethod
    def dict_to_csv_openstack(data: Dict):
        """
        This method supports "openstack" queries.
        """
        file_name = data[0]["metric"]["__name__"] + ".csv"
        with open(file_name, "w", encoding="utf-8") as csv_file:
            line = f'Date Time Hostname {data[0]["metric"]["__name__"]}\n'
            csv_file.write(line)
            for metric in data:
                for i in range(len(metric["values"]) - 1):
                    time = datetime.fromtimestamp(metric["values"][i][0])
                    hostname = metric["metric"]["hostname"]
                    value = metric["values"][i][1]
                    line = f"{time} {hostname} {value}\n"
                    csv_file.write(line)

    @staticmethod
    def dict_to_csv_node(data: Dict):
        """
        This method supports "node" queries.
        """
        file_name = data[0]["metric"]["__name__"] + ".csv"
        with open(file_name, "w", encoding="utf-8") as csv_file:
            line = f'Date Time Hostname {data[0]["metric"]["__name__"]}\n'
            csv_file.write(line)
            for metric in data:
                for i in range(len(metric["values"]) - 1):
                    time = datetime.fromtimestamp(metric["values"][i][0])
                    hostname = gethostbyaddr(
                        metric["metric"]["instance"].split(":")[0]
                    )[0]
                    value = metric["values"][i][1]
                    line = f"{time} {hostname} {value}\n"
                    csv_file.write(line)


if __name__ == "__main__":
    metrics_to_query = [
        "openstack_nova_vcpus_used",
        "openstack_nova_memory_used_bytes",
        "node_hwmon_power_average_watt",
    ]
    endpoint = "http://172.16.102.82:9090/api/v1/query_range"
    RawData(
        metrics_to_query, "1710770960", "1710857376", endpoint
    ).request_to_json_file()
    JsonToCSV(metrics_to_query).json_to_csv()
