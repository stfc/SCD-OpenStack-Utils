from typing import Dict, Tuple
from pathlib import Path
import configparser
import requests
import argparse
from configparser import ConfigParser


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

    for i in [
        "auth.password",
        "auth.username",
        "cloud.instance",
        "db.database",
        "db.host",
    ]:
        assert i in config_dict, f"config file is missing required value {i}"

    return config_dict


def post_to_influxdb(
    data_string: str, host: str, db_name: str, auth: Tuple[str, str]
) -> None:
    """
    This function posts information to influxdb
    :param data_string: data to write
    :param host: hostname and port where influxdb can be accessed
    :param db_name: database name to write to
    :param auth: tuple of username and password to authenticate with influxdb
    """
    print("POSTING TO INFLUX")
    if data_string:
        url = "http://{0}/write?db={1}&precision=s".format(host, db_name)
        r = requests.post(url, data=data_string, auth=auth)
        print(r)
        print(r.text)


def underscore_to_camelcase(input_string: str) -> str:
    """
    This function converts an underscore_delimited_string to camelCase
    :param input_string: underscore_delimited_string
    :return: camelCase string
    """
    words = input_string.split("_")
    camelcase_string = "".join(
        [word.capitalize() if i > 0 else word for i, word in enumerate(words)]
    )
    return camelcase_string


def parse_args(inp_args, description: str = "scrape metrics script") -> Dict:
    """
    This function parses influxdb args from a filepath passed into script when its run.
    The only thing the scripts takes as input is the path to the config file.
    :param description: The description of the script to print on help command
    :param inp_args: input arguments passed when a 'gather metrics' script is run
    :return: args from
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "config_filepath", type=Path, help="Path to influxdb config file"
    )
    args = parser.parse_args(inp_args)

    # Check if the specified config file exists
    if not args.config_filepath.exists():
        parser.error(
            f"The influxdb config file '{args.config_filepath}' does not exist."
        )
    try:
        return read_config_file(args.config_filepath)
    except configparser.Error as exp:
        raise RuntimeError(
            f"could not read influxdb config file '{args.config_filepath}'"
        ) from exp
