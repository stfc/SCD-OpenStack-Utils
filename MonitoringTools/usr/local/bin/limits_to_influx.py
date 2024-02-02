#!/usr/bin/python
import sys
from typing import Dict, List
import json
import openstack
from openstack.identity.v3.project import Project
from send_metric_utils import run_scrape, parse_args
from subprocess import Popen, PIPE


def convert_to_data_string(instance: str, limit_details: Dict) -> str:
    """
    converts a dictionary of values into a data-string influxdb can read
    :param instance: which cloud the info was scraped from (prod or dev)
    :param limit_details: a dictionary of values to convert to string
    :return: a comma-separated string of key=value taken from input dictionary
    """
    data_string = ""
    for project_name, limit_entry in limit_details.items():
        parsed_project_name = project_name.replace(" ", "\ ")
        data_string += (
            f'Limits,Project="{parsed_project_name}",'
            f'instance={instance.capitalize()} '
            f'{get_limit_prop_string(limit_entry)}'
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


def get_limits_for_project(instance, project_id) -> Dict:
    """
    Get limits for a project. This is currently using openstack-cli
    This will be rewritten to instead use openstacksdk
    :param instance: cloud we want to scrape from
    :param project_id: project id we want to collect limits for
    :return: a set of limit properties for project we want
    """
    command = f"openstack --os-cloud={instance} limits show -f json --noindent --absolute --project {project_id}"
    project_limits = json.loads(Popen(command, shell=True, stdout=PIPE).communicate()[0])
    # all limit properties are integers so add 'i' for each value
    return {limit_entry["Name"]: limit_entry["Value"] for limit_entry in project_limits}


def is_valid_project(project: Project) -> bool:
    """
    helper function which returns if project is valid to get limits for
    :param project: project to check
    :return: boolean, True if project should be accounted for in limits
    """
    invalid_strings = ["_rally", "844"]
    return all(s not in project["name"] for s in invalid_strings)


def get_all_limits(instance: str) -> str:
    """
    This function gets limits for each project on openstack
    :param instance: which cloud to scrape from (prod or dev)
    :return: A data string of scraped info
    """
    conn = openstack.connect(cloud=instance)
    limit_details = {
        project["name"]: get_limits_for_project(instance, project["id"])
        for project in conn.list_projects()
        if is_valid_project(project)
    }
    return convert_to_data_string(instance, limit_details)


def main(user_args: List):
    """
    send limits to influx
    :param user_args: args passed into script by user
    """
    influxdb_args = parse_args(user_args, description="Get All Project Limits")
    run_scrape(influxdb_args, get_all_limits)


if __name__ == '__main__':
    main(sys.argv[1:])