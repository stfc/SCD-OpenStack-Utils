#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
"""
Parses results from the rally task report and sends them to influxdb
"""
import json
import sys
import time
from configparser import ConfigParser

import requests

# Read from config file
parser = ConfigParser()
parser.read("/etc/openstack-utils/rally-tester.conf")
host = parser.get("db", "host")
database = parser.get("db", "database")
username = parser.get("auth", "username")
password = parser.get("auth", "password")
instance = parser.get("cloud", "instance")

url = "http://" + host + "/write?db=" + database

nowtime = time.localtime()

workhours = 9 <= nowtime.tm_hour <= 16

with open(sys.argv[1], encoding="utf-8") as data_file:
    data = json.load(data_file)

# pylint: disable=invalid-name
datastring = ""
metrics = []

if isinstance(data, dict):
    print(data)
    for key in data.keys():
        metric = {}
        metric["fields"] = {}
        metric["measurement"] = key
        metric["fields"]["success"] = 0
        metrics.append(metric)
else:
    for test in data:
        for result in test["result"]:
            metric = {}
            metric["fields"] = {}
            metric["measurement"] = test["key"]["name"]

            metric["fields"]["success"] = 1
            for sla in test["sla"]:
                if not sla["success"]:
                    metric["fields"]["success"] = 0

            metric["fields"]["duration"] = result["duration"]
            # metrics.append(metric)
            for atomic_action in result["atomic_actions"]:
                metric["fields"][atomic_action] = result["atomic_actions"][
                    atomic_action
                ]

            metric["fields"]["timestamp"] = result["timestamp"]

            if test["key"]["name"] == "VMTasks.boot_runcommand_delete":
                metric["fields"]["image"] = (
                    '"' + test["key"]["kw"]["args"]["image"]["name"] + '"'
                )
                metric["fields"]["network"] = (
                    '"' + test["key"]["kw"]["args"]["fixednetwork"] + '"'
                )

            metrics.append(metric)

json_metrics = []
for metric in metrics:
    # print metric
    metric["tags"] = {"instance": instance}
    json_metrics.append(metric)
    for field in metric["fields"]:
        datastring += (
            metric["measurement"].replace(".", "-")
            + ",instance="
            + metric["tags"]["instance"]
            + ",workhours="
            + str(workhours)
        )
        datastring += " " + field.replace(".", "-") + "=" + str(metric["fields"][field])
        datastring += "\n"

print(json.dumps(json_metrics, indent=4, sort_keys=True))

print(datastring)

r = requests.post(url, data=datastring, auth=(username, password), timeout=10)
print(r.text)
print(r)
