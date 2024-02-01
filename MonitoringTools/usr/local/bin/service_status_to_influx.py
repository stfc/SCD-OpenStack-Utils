#!/usr/bin/python
import sys
from typing import Dict
import openstack
from openstack.compute.v2.hypervisor import Hypervisor
from openstack.compute.v2.service import Service
from openstack.network.v2.agent import Agent


from send_metric_utils import (
    parse_args,
    post_to_influxdb,
)


def get_hypervisor_properties(hypervisor: Hypervisor) -> Dict:
    """
    This function parses a openstacksdk Hypervisor object to get properties in the correct format
    to feed into influxdb
    :param hypervisor: hypervisor to extract properties from
    :return: A dictionary of useful properties
    """
    hv_prop_dict = {
        "hv": {
            # this is populated by another command
            "aggregate": "no-aggregate",
            "memorymax": hypervisor["memory_size"],
            "memoryused": hypervisor["memory_used"],
            "memoryavailable": hypervisor["memory_free"],
            "cpumax": hypervisor["vcpus"],
            "cpuused": hypervisor["vcpus_used"],
            "cpuavailable": hypervisor["vcpus"] - hypervisor["vcpus_used"],
            "agent": 1,
            "state": 1 if hypervisor["state"] == "up" else 0,
            "statetext": hypervisor["state"].capitalize(),
        }
    }
    return hv_prop_dict


def get_service_properties(service: Service) -> Dict:
    """
    This function parses a openstacksdk Service object to get properties in the correct format
    to feed into influxdb
    :param service: service to extract properties from
    :return: A dictionary of useful properties
    """
    service_prop_dict = {
        service["binary"]: {
            "agent": 1,
            "status": 1 if service["status"] == "enabled" else 0,
            "statustext": service["status"].capitalize(),
            "state": 1 if service["state"] == "up" else 0,
            "statetext": service["state"].capitalize(),
        }
    }
    return service_prop_dict


def get_agent_properties(agent: Agent) -> Dict:
    """
    This function parses a openstacksdk Agent object to get properties in the correct format
    to feed into influxdb
    :param agent: agent to extract properties from
    :return: A dictionary of useful properties
    """
    agent_prop_dict = {
        agent["binary"]: {
            "agent": 1,
            "state": 1 if agent["is_alive"] else 0,
            "statetext": "Up" if agent["is_alive"] else "Down",
            "status": 1 if agent["is_admin_state_up"] else 0,
            "statustext": "Enabled" if agent["is_admin_state_up"] else "Disabled",
        }
    }
    return agent_prop_dict


def convert_to_data_string(service_details: Dict, instance: str) -> str:
    """
    This function creates a data string from service properties to feed into influxdb
    :param service_details: a set of service properties to parse
    :param instance: the cloud instance (prod or dev) that details were scraped from
    :return: A data string of scraped info
    """
    data_string = ""
    for hypervisor_name, services in service_details.items():
        for service_binary, service_stats in services.items():
            data_string += (
                f'ServiceStatus,host="{hypervisor_name}",'
                f'service="{service_binary}",instance={instance.capitalize()} '
                f'{get_service_prop_string(service_stats)}'
            )
    return data_string


def get_service_prop_string(service_dict: Dict) -> str:
    """
    This function is a helper function that creates a partial data string of just the
    properties scraped for a single service
    :param service_dict: properties scraped for a single service
    :return: a data string of scraped info
    """
    stats_strings = []
    for stat, val in service_dict.items():
        parsed_val = val
        if stat not in ["statetext", "statustext", "aggregate"]:
            parsed_val = f"{val}i"
        stats_strings.append(f'{stat}="{parsed_val}"')
    return ",".join(stats_strings)


def get_all_service_statuses(instance: str) -> str:
    """
    This function gets status information for each service node, hypervisor and network
    agent in openstack.
    :param instance: which cloud to scrape from (prod or dev)
    :return: A data string of scraped info
    """
    all_details = {}
    conn = openstack.connect(cloud=instance)
    for hypervisor in conn.list_hypervisors():
        all_details[hypervisor["name"]] = get_hypervisor_properties(hypervisor)

    # populate found hypervisors with what aggregate they belong to - so we can filter by aggregate in grafana
    for aggregate in conn.compute.aggregates():
        for host_name in aggregate["hosts"]:
            if host_name in all_details.keys():
                all_details[host_name]["hv"]["aggregate"] = aggregate["name"]

    for service in conn.compute.services():
        if service["host"] not in all_details.keys():
            all_details[service["host"]] = {}
        all_details[service["host"]] = get_service_properties(service)
        if (
            service["binary"] == "nova-compute"
            and "hv" in all_details[service["host"]].keys()
        ):
            all_details[service["host"]]["hv"]["status"] = all_details[service["host"]][
                service["binary"]
            ]["status"]

    for agent in conn.network.agents():
        if agent["host"] not in all_details.keys():
            all_details[agent["host"]] = {}
        all_details[agent["host"]] = get_agent_properties(agent)
    return convert_to_data_string(all_details, instance)


def main(influxdb_args: Dict):
    """
    send service status to influx
    :param influxdb_args: args to connect to influxdb and openstack to scrape info from
    """
    post_to_influxdb(
        get_all_service_statuses(influxdb_args["cloud.instance"]),
        host=influxdb_args["db.host"],
        db_name=influxdb_args["db.database"],
        auth=(influxdb_args["auth.username"], influxdb_args["auth.password"])
    )


if __name__ == "__main__":
    main(parse_args(sys.argv[1:], description="Get All Service Statuses"))
