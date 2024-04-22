#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
"""
Parses results from the rally task report and sends them to influxdb
"""
import argparse
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import configparser
from configparser import ConfigParser
import requests
from datetime import datetime


def rally_extract_results(report_path: Path, config_path: Path):
    """
    This function reads a rally report file and parses it to get what tests have succeeded/failed
    and sends that information to influxdb
    :param report_path: path to rally report file
    :param config_path: path to file holding influxdb config
    """
    data = read_task_report(report_path)
    config = read_config_file(config_path)
    if isinstance(data, dict):
        metrics = parse_as_dict(data)
    else:
        metrics = []
        for entry in data:
            metrics.extend(parse_test_entry(entry))

    post_to_influxdb(
        build_datastring(metrics, config["cloud.instance"]),
        host=config["db.host"],
        db_name=config["db.database"],
        auth=(config["auth.username"], config["auth.password"]),
    )


def build_datastring(metrics: List, instance: str):
    """
    Helper function that creates a data-string that influxdb can read
    :param metrics: a set of parsed metrics from the rally report file
    :param instance: cloud instance - dev or prod that rally test was run on
    :return:
    """
    data_string = ""
    workhours = 9 <= int(datetime.now().strftime("%H")) <= 16
    for metric in metrics:
        for field in metric["fields"]:
            data_string += (
                f'{metric["measurement"].replate(".", "-")},'
                f',instance={instance}'
                f',workhours={str(workhours)}'
                f'" {field.replace(".", "-")}={str(metric["fields"][field])}\n'
            )
    return data_string


def parse_as_dict(data: Dict) -> List:
    """
    generates metrics for a rally report that is parsed in as a dictionary
    :param data: rally report data read as Dict
    :return: dictionary of metrics for the single rally report
    """
    metrics = []
    for key in data:
        metrics.append({
            "fields": {
                "success": 0
            },
            "measurement": key
        })
    return metrics


def parse_test_entry(test_entry: Dict) -> List:
    """
    generates metrics for a rally report entry
    :param test_entry: a single instance from the rally report
    :return: a set of metrics for that rally report entry
    """
    if len(test_entry["result"]) > 0:
        return parse_entry_multiple_results(test_entry)
    return [parse_entry_single_result(test_entry)]


def parse_entry_multiple_results(test_entry: Dict) -> List[Dict]:
    """
    generates metrics from a rally report entry that contains multiple results
    :param test_entry: a rally report entry that contains multiple results
    :return: a set of metrics for that rally report entry
    """
    metrics = []
    for result in test_entry["result"]:
        # grab default metrics for the entry that gets modified later for each separate result
        metric = parse_entry_single_result(test_entry)

        for atomic_action in result["atomic_action"]:
            metric["fields"][atomic_action] = result["atomic_actions"][atomic_action]
        metric["fields"]["timestamp"] = result["timestamp"]
    return metrics


def parse_entry_single_result(test_entry: Dict) -> Dict:
    """
    generates metrics from a rally report entry that contains single result
    :param test_entry: a rally report entry that contains a single result entry
    :return: a set of metrics for that rally report entry
    """
    success_flag = 1
    if test_entry["sla"]:
        success_flag = int(all(sla["success"] for sla in test_entry["sla"]))

    metric = {
        "fields": {
            "success": success_flag,
            "duration": test_entry["full_duration"],
            "timestamp": datetime.strptime(
                test_entry['created_at'],
                '%Y-%d-%mT%H:%M:%S'
            ).timestamp() * 1000
        },
        "measurement": test_entry["key"]["name"]
    }

    if test_entry["key"]["name"] == "VMTasks.boot_runcommand_delete":
        metric["fields"]["image"] = (
            f'"{test_entry["key"]["kw"]["args"]["image"]["name"]}"'
        )
        metric["fields"]["network"] = (
            f'"{test_entry["key"]["kw"]["args"]["fixednetwork"]}"'
        )
    return metric


def read_task_report(report_path: Path) -> Optional[List, Dict]:
    """
    This function reads a rally task report and returns a dictionary of results
    :param report_path: path to rally task report file
    :return: dictionary containing info held in rally task report file
    """
    with open(report_path, encoding="utf-8") as data_file:
        data = json.load(data_file)
    assert data, "No data found in given path"
    return data


def read_config_file(config_filepath: Path) -> Dict:
    """
    This function reads a config file and puts it into a dictionary
    :param config_filepath:
    :return: A flattened dictionary containing key-value pairs from config file
    """
    config = ConfigParser()
    config.read(config_filepath)
    config_dict = {}
    for section in config.sections():
        for key, value in config.items(section):
            config_dict[f"{section}.{key}"] = value

    required_values = [
        "auth.password",
        "auth.username",
        "cloud.instance",
        "db.database",
        "db.host",
    ]
    assert all(
        val in config_dict for val in required_values
    ), "Config file is missing required values."
    return config_dict


def post_to_influxdb(
    data_string: str, host: str, db_name: str, auth: Tuple[str, str]
) -> None:
    """
    This function posts information to influxdb
    :param data_string: data to write
    :param host: hostname and port where influxdb can be accessed
    :param db_name: database name to write to
    :param auth: tuple of (username, password) to authenticate with influxdb
    """
    if not data_string:
        return

    url = f"http://{host}/write?db={db_name}"
    response = requests.post(url, data=data_string, auth=auth, timeout=60)
    response.raise_for_status()


def main(user_args: List):
    config_path = Path("/etc/openstack-utils/rally-tester.conf")
    parser = argparse.ArgumentParser(description="send rally report to influx")
    parser.add_argument(
        "rally_filepath", type=Path, help="Path to rally report file"
    )
    try:
        args = parser.parse_args(user_args)
    except argparse.ArgumentTypeError as exp:
        raise RuntimeError("Error reading input arguments") from exp

    if not args.rally_filepath.is_file():
        raise RuntimeError(f"Invalid filepath given '{args.config_filepath}'")

    try:
        read_config_file(config_path)
    except configparser.Error as exp:
        raise RuntimeError(
            f"could not read influx db config file '{args.config_filepath}'"
        ) from exp

    rally_extract_results(args.rally_filepath, config_path)


if __name__ == "__main__":
    main(sys.argv[1:])
