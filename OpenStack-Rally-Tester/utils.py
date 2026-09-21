import json
import os
import time
from configparser import ConfigParser

def load_data(filename):
    """Load JSON data from a file."""
    with open(filename, encoding="utf-8") as data_file:
        return json.load(data_file)


def load_config(config_path: str):
    """ loads influx config from config file and environment variables """

    config = {}

    parser = ConfigParser()
    if not parser.read(config_path, encoding="utf-8"):
        raise FileNotFoundError(f"Config file {config_path} not found")

    config["host"] = parser.get("db", "host")
    config["port"] = parser.get("db", "port")
    config["database"] = parser.get("db", "database")
    config["instance"] = parser.get("cloud", "instance")

    def require_env(name: str) -> str:
        """
        helper to load in environment variables
        :param name: environment variable name
        :return: environment variable value
        """
        value = os.getenv(name)
        if not value:
            raise ValueError(f"{name}: influxdb environment variable not set")
        return value

    config["username"] = require_env("INFLUXDB_USERNAME")
    config["password"] = require_env("INFLUXDB_PASSWORD")
    return config


def create_metric(measurement, fields):
    """Create a metric dictionary."""
    return {
        "measurement": measurement,
        "fields": fields,
    }

def add_tags(metrics, instance):
    """Add instance tag to each metric."""
    for metric in metrics:
        metric["tags"] = {"instance": instance}
    return metrics

def is_workhour() -> bool:
    """Returns if it is currently a work hour."""
    nowtime = time.localtime()
    return 9 <= nowtime.tm_hour <= 16
