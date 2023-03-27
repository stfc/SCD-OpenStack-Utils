"""
Provides utility functions to collect energy usage information
"""
import subprocess
import time
import os
from pathlib import Path
import re
from typing import Dict
import logging

logger = logging.getLogger(__name__)


def retry(
    retry_on: (Exception,) = None,
    retries: int = 3,
    delay: int = 3,
    backoff: int = 2,
    retry_logger: logging.Logger = None,
):
    """A retry decorator

    Keyword Arguments:
        retry_on: a set of exceptions that when any occur, will trigger a retry
        retries: number of retries to perform before returning None
        delay: number of seconds delay before next retry
        backoff: a factor to increase delay after every fail
        retry_logger: logger to log failed attempts
    """

    def decorator(func):
        def inner(*args, **kwargs):
            res = None
            for i in range(retries + 1):
                try:
                    res = func(*args, **kwargs)
                    break
                except retry_on:
                    if i == retries:
                        if retry_logger:
                            retry_logger.error(
                                "function failed and max retries %s exceeded", retries
                            )
                        return None
                seconds = delay + (backoff * i)
                if retry_logger:
                    retry_logger.warning(
                        "function failed to run. Failed attempts: %s. Retrying after %s delay",
                        i + 1,
                        seconds,
                    )
                time.sleep(seconds)
            return res

        return inner

    return decorator


@retry(retry_on=(AssertionError,), retries=3, delay=3, backoff=2, retry_logger=logger)
def run_cmd(cmd_args: str):
    """Run a bash command with given arguments and return output

    Keyword Arguments
        cmd_args: a string representing bash command to run
    """
    with subprocess.Popen(
        cmd_args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as out:
        # assert we did not find any errors
        assert not out.stderr.read().decode()
        res_out = out.stdout.read().decode()
    return res_out


def check_ipmi_conn():
    """Check if IPMItool exists and can be connected to

    Checks if device exists at any of these locations /dev/ipmi0, /dev/ipmi/0 or /dev/ipmidev/0
    which imply that ipmi-dcmi can be used to get power info
    """
    res = any(Path(f).exists() for f in ["/dev/ipmi0", "/dev/ipmi/0", "/dev/ipmidev/0"])
    if not res:
        logger.error("Failed to find ipmi device on host")
    return res


def ipmi_raw_power_query():
    """
    Get raw power query from IPMItool

    Calls ipmi-dcmi command to get all power statistics
    """
    try:
        return run_cmd("/usr/sbin/ipmi-dcmi --get-system-power-statistics")
    except AssertionError:
        logger.error(
            "command '/usr/sbin/ipmi-dcmi --get-system-power-statistics failed"
        )
        return None


def to_csv(stats: Dict, include_header: bool = False):
    """convert dictionary into csv string

    Keyword arguments
    stats -- dict, key-value pairs to be returned in csv format
    include_header, bool, flag to set if dictionary keys should be returned as header
    """
    res = ",".join([str(s) for s in stats.values()])
    if include_header:
        return f"{','.join(stats.keys())}\n{res}"
    return res


def get_ipmi_power_stats(*args):
    """Get ipmi power stats as dictionary.

    Keyword arguments
    *args -- a set of fields to parse and collect.
    can be one or more of:
        "current_power": instantaneous reading in Watts,
        "minimum_power_over_sampling_duration: minimum Watt reading from last sample till now
        "maximum_power_over_sampling_duration": maximum Watt reading from last sample till now
        "average_power_over_sampling_duration": average Watt reading from last sample till now
        "statistics_reporting_time_period": sample period in milliseconds
        "time_stamp": current timestamp for reading taken
        "power_measurement": whether power measurement is active on host
    """
    if not check_ipmi_conn():
        return None
    res = ipmi_raw_power_query()

    power_stats = {x: "" for x in args}

    if res:
        for line in res.splitlines():
            line_str = line.split(":")
            stat = line_str[0].strip().lower().replace(" ", "_")
            raw_val = ":".join(line_str[1:]).strip()

            if stat in power_stats.keys():
                if stat == "time_stamp":
                    stat_val = re.search(
                        r"\d{2}/\d{2}/\d{4}\s-\s\d{2}:\d{2}:\d{2}", raw_val
                    ).group(0)

                elif stat == "power_measurement":
                    stat_val = raw_val

                else:
                    stat_val = re.search("[0-9]+", raw_val).group(0)

                power_stats[stat] = stat_val

    return power_stats


def get_os_load(*args):
    """
    get os load average from os library

    Keyword Arguments
    args -- a set of fields to parse and collect.
    can be one or more of:
        "os_load_1": avg os load last 1 minute,
        "os_load_5": avg os load last 5 minutes,
        "os_load_15: avg os loat last 15 minutes"
    """
    res = {x: "" for x in args}

    stats = {"os_load_1": "", "os_load_5": "", "os_loads_15": ""}

    try:
        stats["os_load_1"], stats["os_load_5"], stats["os_load_15"] = os.getloadavg()
    except OSError:
        pass

    res.update({k: v for k, v in stats.items() if k in args})
    return res


def get_ram_usage(*args):
    """Get Ram usage stats

    Keyword Arguments
    args -- a set of fields to parse and collect.
    can be one or more of:
        "max_ram_kb",
        "used_ram_kb",
        "ram_usage_percentage": (Used RAM / Total RAM) * 100
    """
    res = {x: "" for x in args}

    stats = {"max_ram_kb": "", "used_ram_kb": "", "ram_usage_percentage": ""}

    try:
        stats["max_ram_kb"] = int(
            run_cmd("free -k | sed -n '2p' | awk '{print $2}'"),
        )
        stats["used_ram_kb"] = int(
            run_cmd("free -k | sed -n '2p' | awk '{print $2}'"),
        )

        if stats["max_ram_kb"] and stats["used_ram_kb"]:
            stats["ram_usage_percentage"] = round(
                (stats["used_ram_kb"] / stats["max_ram_kb"]) * 100, 3
            )

    except (AssertionError, ValueError):
        pass

    res.update({k: v for k, v in stats.items() if k in args})
    return res
