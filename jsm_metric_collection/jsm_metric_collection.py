import argparse
import json
import sys
from time import sleep

import requests
import requests.exceptions
import pandas as pd
from requests.auth import HTTPBasicAuth


def parse_args(inp_args):
    """
    Function to parse commandline args
    :param inp_args: a set of commandline args to parse (dict)
    :returns: A dictionary of parsed args
    """
    # Get arguments passed to the script
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-u",
        "--username",
        metavar="USERNAME",
        help="FedID of the user",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--password",
        metavar="PASSWORD",
        help="Password of the user",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="OUTPUT",
        help="Directory to create the output files in",
        default="output",
    )
    args = parser.parse_args(inp_args)
    return args


def get_response_json(auth, headers, url):

    session = requests.session()
    session.headers = headers
    session.auth = auth

    while True:
        response = session.get(url)
        if response.content != b'{"status":"RUNNING"}':
            break
        else:
            sleep(1)

    return json.loads(response.text)


def get_report_task_id(auth, headers, host, query):
    url = f"{host}/rest/servicedesk/reports/1/reports/async/STFCCLOUD/{query}"

    json_load = get_response_json(auth, headers, url)

    return json_load.get("taskId")


def get_issues_amount(auth, headers, host):

    return_amount = 50
    issues_amount = 0
    while return_amount == 50:
        url = f"{host}/rest/servicedeskapi/servicedesk/6/queue/59/issue?start={issues_amount}"

        json_load = get_response_json(auth, headers, url)

        return_amount = json_load.get("size")
        issues_amount = issues_amount + return_amount

    return issues_amount


def get_report_values(auth, headers, host, job_id):
    url = f"{host}/rest/servicedesk/reports/1/reports/async/STFCCLOUD/32/poll?jobID={job_id}"

    json_load = get_response_json(auth, headers, url)
    values = []

    for series in json_load.get("reportDataResponse").get("series"):
        values.append(series.get("seriesSummaryValue"))

    return values


def get_customer_satisfaction(auth, headers, host, time_series):
    url = f"{host}/rest/servicedesk/1/projects/STFCCLOUD/report/feedback?start=0&limit=20&jsonFilter={{" \
          f"%22timescaleId%22%3A{time_series}}}&expand=overall "

    json_load = get_response_json(auth, headers, url)

    return [json_load.get("summary").get("average"), json_load.get("summary").get("count")]


def jsm_metric_collection():
    args = parse_args(sys.argv[1:])
    host = "https://stfc.atlassian.net"
    username = args.username
    password = args.password

    auth = HTTPBasicAuth(username, password)
    headers = {
        "Accept": "application/json",
    }

    issues_amount = get_issues_amount(auth, headers, host)

    weekly_cvr_task_id = get_report_task_id(auth, headers, host, "32?timescaleId=2")
    weekly_created_vs_resolved = get_report_values(auth, headers, host, weekly_cvr_task_id)

    monthly_cvr_task_id = get_report_task_id(auth, headers, host, "32?timescaleId=4")
    monthly_created_vs_resolved = get_report_values(auth, headers, host, monthly_cvr_task_id)

    weekly_sla_task_id = get_report_task_id(auth, headers, host, "36?timescaleId=2")
    weekly_sla = get_report_values(auth, headers, host, weekly_sla_task_id)

    monthly_sla_task_id = get_report_task_id(auth, headers, host, "36?timescaleId=4")
    monthly_sla = get_report_values(auth, headers, host, monthly_sla_task_id)

    weekly_customer_satisfaction = get_customer_satisfaction(auth, headers, host, 2)
    monthly_customer_satisfaction = get_customer_satisfaction(auth, headers, host, 4)

    print(issues_amount)
    print(weekly_created_vs_resolved)
    print(monthly_created_vs_resolved)
    print(weekly_sla)
    print(monthly_sla)
    print(weekly_customer_satisfaction)
    print(monthly_customer_satisfaction)


if __name__ == '__main__':
    jsm_metric_collection()
