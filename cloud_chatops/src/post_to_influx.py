from src.get_github_prs import GetGitHubPRs
from src.read_data import get_token, get_repos
from typing import Dict, List
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from time import time_ns

"""
This module is simply for interest and serves no functional purpose.
It collects the count of open pull requests in each repository and
sends that data along with a timestamp to an InfluxDB instance.
Provided this service is run for a long period of time we might see some interesting trends in data.
For example, new starters in the Cloud or public holidays.
"""


class PostDataToInflux:
    """
    This class will post the count of open PRs in each repo to InfluxDB.
    """

    def __init__(self):
        self.host = "http://172.16.110.166:8086"
        self.org = "cloud"
        self.bucket = "slack_app"
        self.token = get_token("INFLUX_TOKEN")
        self.client = influxdb_client.InfluxDBClient(
            url=self.host, org=self.org, token=self.token
        )

    def run(self) -> None:
        """
        This method is the entry point of the class and makes the points then writes the data.
        """
        prs = GetGitHubPRs(get_repos()).run()
        points = self.create_data_points(prs)
        self.write_to_influx(points)

    def write_to_influx(self, points: List[influxdb_client.Point]) -> None:
        """
        This method writes to the Influx database each point it is given.
        :param points: The data points to write to Influx
        """
        with self.client.write_api(write_options=SYNCHRONOUS) as write_api:
            for p in points:
                write_api.write(record=p, bucket=self.bucket, org=self.org)

    @staticmethod
    def create_data_points(prs: Dict[str, List]) -> List[influxdb_client.Point]:
        """
        This method creats an Influx Point object for each PR and returns a list of those objects.
        :param prs: PRs to create points from.
        :return: List of Influx point objects.
        """
        data_points = []
        for repo in prs.keys():
            point = (
                influxdb_client.Point("repository_pr_count")
                .tag("repository", repo)
                .field("no-prs", len(prs[repo]))
                .time(time_ns())
            )
            data_points.append(point)
        return data_points
