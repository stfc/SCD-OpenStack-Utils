from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
from sys import argv
from time import sleep

import csv
import json
import requests
import requests.auth
import xlsxwriter


def parse_args(inp_args):
    """
    Function to parse commandline args
    :param inp_args: a set of commandline args to parse (dict)
    :returns: A dictionary of parsed args
    """
    # Get arguments passed to the script
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter
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
        if response.content != b'{"status":"RUNNING"}' and response.content != b'{"status":"ENQUEUED"}':
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

    return [issues_amount]


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


def generate_xlsx_file(filepath):
    jsm_data = list(csv.reader(open("data.csv")))
    data_len = len(jsm_data)
    titles = ("Date", "Issues", "Created Weekly", "Resolved Weekly", "SLA Weekly", "Average Review Weekly",
              "Reviews Weekly", "Created Monthly", "Resolved Monthly", "SLA Monthly", "Average Review Monthly",
              "Reviews Monthly")

    workbook = xlsxwriter.Workbook(filepath, {"strings_to_numbers": True})
    jsm_data_worksheet = workbook.add_worksheet("JSM Data")

    date_format = workbook.add_format({"num_format": "dd/mm/yyyy"})
    percentage_format = workbook.add_format({"num_format": "0.00%"})

    jsm_data_worksheet.add_table(f"A1:L{data_len + 1}", {"data": jsm_data,
                                                         "style": "Table Style Light 15",
                                                         "columns": [{"header": titles[0],
                                                                      "format": date_format},
                                                                     {"header": titles[1]},
                                                                     {"header": titles[2]},
                                                                     {"header": titles[3]},
                                                                     {"header": titles[4],
                                                                      "format": percentage_format},
                                                                     {"header": titles[5]},
                                                                     {"header": titles[6]},
                                                                     {"header": titles[7]},
                                                                     {"header": titles[8]},
                                                                     {"header": titles[9],
                                                                      "format": percentage_format},
                                                                     {"header": titles[10]},
                                                                     {"header": titles[11]},
                                                                     ]
                                                         })

    jsm_data_worksheet.autofit()

    graph_worksheet = workbook.add_worksheet("JSM Graphs")

    for i in range(len(titles) - 1):
        chart = workbook.add_chart({"type": "line"})
        chart.add_series({"categories": f"='JSM Data'!$A$2:$A${data_len + 1}",
                          "values": f"='JSM Data'!${chr(i + 66)}$2:${chr(i + 66)}${data_len + 1}"})
        chart.set_x_axis({"name": "Date"})
        chart.set_title({"name": titles[i + 1]})
        chart.set_legend({"none": True})
        graph_worksheet.insert_chart(f"{chr(66 + (8 * (i % 3)))}{2 + (16 * (i // 3))}", chart)

    workbook.close()


def save_csv(jsm_data):
    data_not_exists = True

    open("data.csv", "a+")

    with open("data.csv", "r", newline="") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if row[0] == jsm_data[0]:
                data_not_exists = False

    if data_not_exists:
        with open("data.csv", "a+", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(jsm_data)


def jsm_metric_collection():
    args = parse_args(argv[1:])
    host = "https://stfc.atlassian.net"
    username = args.username
    password = args.password

    auth = requests.auth.HTTPBasicAuth(username, password)
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

    jsm_data = [datetime.today().date().strftime("%Y-%m-%d")] + \
               issues_amount + weekly_created_vs_resolved + weekly_sla + \
               weekly_customer_satisfaction + monthly_created_vs_resolved + \
               monthly_sla + monthly_customer_satisfaction

    save_csv(jsm_data)

    generate_xlsx_file("test.xlsx")


if __name__ == '__main__':
    jsm_metric_collection()
