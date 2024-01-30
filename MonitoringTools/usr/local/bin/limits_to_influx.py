#!/usr/bin/python
import sys
from typing import Dict
import time
import openstack
from send_metric_utils import parse_args, post_to_influxdb, underscore_to_camelcase


def parse_compute_limits(compute_limit_dict: Dict) -> Dict:
    """
    parse compute limits dict to extract properties we want in correct format
    :param compute_limit_dict: a dictionary holding compute limits
    :return: Dict of useful properties
    """
    compute_limits = {
        # need to convert to limit name camelCase as that's what influx is expecting
        underscore_to_camelcase(k): v for k, v in compute_limit_dict.items()
        # add limit 'properties' later - as this is nested and already in camelCase
        if k not in ["location", "properties"]
    }
    compute_limits.update(compute_limit_dict["properties"])
    return compute_limits


def convert_to_data_string(limit_details: Dict, instance: str) -> str:
    """
    converts a dictionary of values into a data-string influxdb can read
    :param limit_details: a dictionary of values to convert to string
    :param instance: which cloud the info was scraped from (prod or dev)
    :return: a comma-separated string of key=value taken from input dictionary
    """
    data_string = ""
    for project_name, limit_details in limit_details.items():
        parsed_project_name = project_name.replace(" ", "\ ")
        data_string += (
            f'Limits,Project="{parsed_project_name}",'
            f'instance={instance.capitalize()} '
            f'{get_limit_prop_string(limit_details)}'
        )
    return data_string


def get_limit_prop_string(limit_details):
    """
    This function is a helper function that creates a partial data string of just the
    properties scraped for a single service
    :param limit_details: properties scraped for a single project
    :return: a data string of scraped info
    """
    # all limit properties are integers so add 'i' for each value
    return ",".join([f"{limit}={val}i" for limit, val in limit_details.items()])


def get_all_limits(instance: str) -> str:
    """
    This function gets limits for each project on openstack
    :param instance: which cloud to scrape from (prod or dev)
    :return: A data string of scraped info
    """
    conn = openstack.connect(cloud=instance)

    projects_list = [
        proj for proj in conn.list_projects()
        if all(s not in proj["name"] for s in ("_rally", "844"))
    ]

    limit_details = {}
    print(len(projects_list))
    for i, project in enumerate(projects_list, 1):

        project_details = {
            **parse_compute_limits(conn.get_compute_limits(project["id"])),
            **conn.get_volume_limits(project["id"])["absolute"]
        }
        print(i)
        limit_details[project["name"]] = project_details
    return convert_to_data_string(limit_details, instance)


def main(influxdb_args: Dict):
    """
    send limits to influx
    :param influxdb_args: args to connect to influxdb and openstack to scrape info from
    """
    post_to_influxdb(
        get_all_limits(influxdb_args["cloud.instance"]),
        host=influxdb_args["db.host"],
        db_name=influxdb_args["db.database"],
        auth=(influxdb_args["auth.username"], influxdb_args["auth.password"])
    )


if __name__ == '__main__':
    main(parse_args(sys.argv[1:], description="Get All Project Limits"))
