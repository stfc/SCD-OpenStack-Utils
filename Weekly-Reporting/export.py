"""Export weekly reports statistics data to an InfluxDB bucket."""

from pprint import pprint
from typing import Dict, List

from influxdb_client import Point
from pathlib import Path
import argparse
import yaml
import configparser
import logging
import datetime

from influxdb_client.client import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

time = datetime.datetime.now().isoformat()
# time = "2025-01-02T15:17:37.780483"


def main(args: argparse.Namespace):
    """
    Main entry point to script.
    :param args: Arguments provided on the command line.
    """
    _check_args(args)
    points = []
    if args.report_file:
        points = _create_points_report(args.report_file)
    elif args.inventory_file:
        points = _create_points_inventory(args.inventory_file)
    api_token = _get_token(args.token_file)
    _write_data(
        points=points, host=args.host, org=args.org, bucket=args.bucket, token=api_token
    )


def _check_args(args: argparse.Namespace):
    """
    Check the correct arguments are provided
    :param args: Argparse namespace
    """
    if not args.host:
        raise RuntimeError("Argument --host not given.")
    if not args.org:
        raise RuntimeError("Argument --org not given.")
    if not args.bucket:
        raise RuntimeError("Argument --bucket not given.")
    if not args.token_file:
        raise RuntimeError("Argument --token-file not given.")
    if not args.report_file and not args.inventory_file:
        raise RuntimeError("Argument --report-file or --inventory-file not given.")
    if args.report_file and args.inventory_file:
        raise RuntimeError(
            "Argument --report-file and --inventory-file given. Only one data file can be provided."
        )
    if not Path(args.token_file).is_file():
        raise RuntimeError(f"Cannot find token file at path {args.token_file}.")
    if args.report_file and not Path(args.report_file).is_file():
        raise RuntimeError(f"Cannot find report file at path {args.report_file}.")
    if args.inventory_file and not Path(args.inventory_file).is_file():
        raise RuntimeError(f"Cannot find inventory file at path {args.inventory_file}.")


def _get_token(file_path: str) -> str:
    """
    Get the token from the token file.
    :param file_path: File path to token file
    :return: Token as string
    """
    with open(Path(file_path), "r", encoding="utf-8") as file:
        token = file.read().strip()
    return token


def _create_points_report(file_path: str) -> List[Point]:
    """
    Create a list of Influx points from the data.
    :param file_path: Path to data file
    :return: List of Points.
    """
    points = []
    with open(Path(file_path), "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    for key, value in data.items():
        points += _from_key(key, value)

    return points


def _create_points_inventory(file_path: str) -> List[Point]:
    """
    Create a list of Influx points from the data.
    :param file_path: Path to data file
    :return: List of Points.
    """
    points = []
    config = configparser.ConfigParser()
    config.read(file_path)
    pprint(config)

    return points


def _from_key(key: str, data: Dict) -> List[Point]:
    """
    Decide which create_point method to call from the key.
    :param key: Section of data. For example, CPU
    :param data: The values of the section
    :return: List of points
    """
    if key == "cpu":
        return _from_cpu(data)
    if key == "memory":
        return _from_memory(data)
    if key == "storage":
        return _from_storage(data)
    if key == "hv":
        return _from_hv(data)
    if key == "vm":
        return _from_vm(data)
    if key == "floating_ip":
        return _from_fip(data)
    if key == "virtual_worker_nodes":
        return _from_vwn(data)
    else:
        raise RuntimeError(
            f"Key {key} not supported. Please contact service maintainer."
        )


def _from_cpu(data: Dict) -> List[Point]:
    """Extract cpu data from yaml into a Point."""
    return [
        Point("cpu")
        .field("in_use", data["in_use"])
        .field("total", data["total"])
        .time(time)
    ]


def _from_memory(data: Dict) -> List[Point]:
    """Extract memory data from yaml into a Point."""

    return [
        Point("memory")
        .field("in_use", data["in_use"])
        .field("total", data["total"])
        .time(time)
    ]


def _from_storage(data: Dict) -> List[Point]:
    """Extract storage data from yaml into Points."""
    points = []
    for key, value in data.items():
        for key_2, value_2 in value.items():
            points.append(Point(key).field(key_2, value_2).time(time))
    return points


def _from_hv(data: Dict) -> List[Point]:
    """Extract hv data from yaml into Points."""
    points = []
    points.append(Point("hv").field("active", data["active"]["active"]).time(time))
    points.append(
        Point("hv").field("active_and_cpu_full", data["active"]["cpu_full"]).time(time)
    )
    points.append(
        Point("hv")
        .field("active_and_memory_full", data["active"]["memory_full"])
        .time(time)
    )
    points.append(Point("hv").field("down", data["down"]).time(time))
    points.append(Point("hv").field("disabled", data["disabled"]).time(time))
    return points


def _from_vm(data: Dict) -> List[Point]:
    """Extract vm data from yaml into a Point."""
    return [
        (
            Point("vm")
            .field("active", data["active"])
            .field("shutoff", data["shutoff"])
            .field("errored", data["errored"])
            .field("building", data["building"])
            .time(time)
        )
    ]


def _from_fip(data: Dict) -> List[Point]:
    """Extract floating ip data from yaml into a Point."""
    return [
        Point("floating_ip")
        .field("in_use", data["in_use"])
        .field("total", data["total"])
        .time(time)
    ]


def _from_vwn(data: Dict) -> List[Point]:
    """Extract virtual worker nodes data from yaml into a Point."""
    return [Point("virtual_worker_nodes").field("active", data["active"]).time(time)]


def _write_data(points: List[Point], host: str, org: str, bucket: str, token: str):
    """
    Write the data to the InfluxDB bucket.
    :param points: Points to write
    :param host: Host URL
    :param org: InfluxDB organisation
    :param bucket: InfluxDB bucket
    :param token: InfluxDB API access token
    """
    with influxdb_client.InfluxDBClient(url=host, token=token, org=org) as _client:
        with _client.write_api(write_options=SYNCHRONOUS) as _write_api:
            _write_api.write(bucket, org, points)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="InfluxDB host url with port.")
    parser.add_argument("--org", help="InfluxDB organisation.")
    parser.add_argument("--bucket", help="InfluxDB bucket to write to.")
    parser.add_argument("--token-file", help="InfluxDB access token file path.")
    parser.add_argument("--report-file", help="Report yaml file.")
    parser.add_argument("--inventory-file", help="Inventory ini file.")
    arguments = parser.parse_args()
    main(arguments)
