from src.get_github_prs import GetGitHubPRs
from src.read_data import get_token, get_repos
from typing import Dict, List
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from time import time_ns


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

    def run(self):
        prs = GetGitHubPRs(get_repos()).run()
        self.write_to_influx(prs)

    def write_to_influx(self, prs: Dict[str, List]):
        data_points = []
        for repo in prs.keys():
            point = (
                influxdb_client.Point("repository_pr_count")
                .tag("repository", repo)
                .field("no-prs", len(prs[repo]))
                .time(time_ns())
            )
            data_points.append(point)
        with self.client.write_api(write_options=SYNCHRONOUS) as write_api:
            for p in data_points:
                write_api.write(record=p, bucket=self.bucket, org=self.org)
