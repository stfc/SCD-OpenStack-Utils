from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
from pathlib import Path
from sys import argv
from time import sleep
from os import path

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
    """
    Function to send a get request to a url and return the response as json
    :param auth: A HTTPBasicAuth object for authentication (HTTPBasicAuth)
    :param headers: A request Header (dict)
    :param url: The URL to send the request (string)
    :returns: A dictionary of JSON values
    """
    session = requests.session()
    session.headers = headers
    session.auth = auth

    attempts = 5

    while attempts > 0:
        response = session.get(url, timeout=5)
        if response.content != b'{"status":"RUNNING"}' and response.content != b'{"status":"ENQUEUED"}':
            break
        else:
            sleep(1)
            attempts = attempts-1

    if attempts == 0:
        raise requests.exceptions.Timeout("Get request status not completed before timeout")

    return json.loads(response.text)


def get_report_task_id(auth, headers, host, query):
    """
    Function to get a report task ID so that task can be queried
    :param auth: A HTTPBasicAuth object for authentication (HTTPBasicAuth)
    :param headers: A request Header (dict)
    :param host: The host used to create the URL to send the request (string)
    :param query: The section of the URL that signifies the task
    :returns: A string containing the task ID
    """
    url = f"{host}/rest/servicedesk/reports/1/reports/async/STFCCLOUD/{query}"

    json_load = get_response_json(auth, headers, url)

    return json_load.get("taskId")


def get_issues_amount(auth, headers, host):
    """
    Function to get the number of issues using a loop, as only 50 can be checked at a time
    :param auth: A HTTPBasicAuth object for authentication (HTTPBasicAuth)
    :param headers: A request Header (dict)
    :param host: The host used to create the URL to send the request (string)
    :returns: A list with only a string containing the number of issues
    """
    return_amount = 50
    issues_amount = 0
    while return_amount == 50:
        url = f"{host}/rest/servicedeskapi/servicedesk/6/queue/59/issue?start={issues_amount}"

        json_load = get_response_json(auth, headers, url)

        return_amount = json_load.get("size")
        issues_amount = issues_amount + return_amount

    return [issues_amount]


def get_report_values(auth, headers, host, job_id):
    """
    Function to get the value in a custom report using a job ID
    :param auth: A HTTPBasicAuth object for authentication (HTTPBasicAuth)
    :param headers: A request Header (dict)
    :param host: The host used to create the URL to send the request (string)
    :param job_id: A string containing the ID of the report
    :returns: A list with only a string containing the number of issues
    """
    url = f"{host}/rest/servicedesk/reports/1/reports/async/STFCCLOUD/32/poll?jobID={job_id}"

    json_load = get_response_json(auth, headers, url)
    values = []

    for series in json_load.get("reportDataResponse").get("series"):
        values.append(series.get("seriesSummaryValue"))

    return values


def get_customer_satisfaction(auth, headers, host, time_series):
    """
    Function to get the customer satisfaction over a period of time
    :param auth: A HTTPBasicAuth object for authentication (HTTPBasicAuth)
    :param headers: A request Header (dict):
    :param host: The host used to create the URL to send the request (string)
    :param time_series: A string containing the timescale to check
    :returns: A list with the ints for the number of issues created and resolved in a period
    """
    url = f"{host}/rest/servicedesk/1/projects/STFCCLOUD/report/feedback?start=0&limit=20&jsonFilter={{" \
          f"%22timescaleId%22%3A{time_series}}}&expand=overall "

    json_load = get_response_json(auth, headers, url)

    return [json_load.get("summary").get("average"), json_load.get("summary").get("count")]


def save_csv(jsm_data, csv_output_location):
    """
    Function to create a csv file or append to one with a line of data
    :param jsm_data: A list of all the data gotten (list)
    :param csv_output_location: The location of the csv output file (string)
    """
    data_exists = False

    open(csv_output_location, "a+")

    with open(csv_output_location, "r", newline="") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if row[0] == jsm_data[0]:
                data_exists = True

    if not data_exists:
        with open(csv_output_location, "a+", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(jsm_data)


def generate_xlsx_file(csv_output_location, xlsx_output_location):
    """
    Function to generate an Excel file using a csv file
    :param csv_output_location: The location of the csv output file (string)
    :param xlsx_output_location: The location of the Excel output file (string)
    """
    jsm_data = list(csv.reader(open(csv_output_location)))

    titles = ("Date", "Issues", "Created Weekly", "Resolved Weekly", "SLA Weekly", "Average Review Weekly",
              "Reviews Weekly", "Created Monthly", "Resolved Monthly", "SLA Monthly", "Average Review Monthly",
              "Reviews Monthly")

    workbook = xlsxwriter.Workbook(xlsx_output_location, {"strings_to_numbers": True})

    generate_jsm_data_page(workbook, jsm_data, titles)

    generate_jsm_graph_page(workbook, jsm_data, titles)

    workbook.close()


def generate_jsm_data_page(workbook, jsm_data, titles):
    """
    Function to generate page with a table containing data from a csv file for an excel file
    :param workbook: The workbook in which to create the page (workbook)
    :param jsm_data: The data from a csv file (list)
    :param titles: The titles of the columns to be used for the table (list)
    """
    jsm_data_worksheet = workbook.add_worksheet("JSM Data")

    date_format = workbook.add_format({"num_format": "dd/mm/yyyy"})
    percentage_format = workbook.add_format({"num_format": "0.00%"})

    jsm_data_worksheet.add_table(
        f"A1:L{len(jsm_data) + 1}",
        {"data": jsm_data,
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


def generate_jsm_graph_page(workbook, jsm_data, titles):
    """
    Function to generate page with a table containing data from a csv file for an excel file
    :param workbook: The workbook in which to create the page (workbook)
    :param jsm_data: The data from a csv file (list)
    :param titles: The titles to be used for the graphs (list)
    """
    graph_worksheet = workbook.add_worksheet("JSM Graphs")

    for i in range(len(titles) - 1):
        chart = workbook.add_chart({"type": "line"})
        chart.add_series({
            "categories": f"='JSM Data'!$A$2:$A${len(jsm_data) + 1}",
            "values": f"='JSM Data'!${chr(i + 66)}$2:${chr(i + 66)}${len(jsm_data) + 1}",
            "marker": {"type": "circle"},
        })
        chart.set_x_axis({"name": "Date"})
        chart.set_title({"name": titles[i + 1]})
        chart.set_legend({"none": True})
        graph_worksheet.insert_chart(f"{chr(66 + (8 * (i % 3)))}{2 + (16 * (i // 3))}", chart)


def jsm_metric_collection():
    """
    Main function to query the Service Desk for data, combine the data and save is in a CSV format and then
    take that csv file to generate an excel spreadsheet for easy viewing of that data over time.
    """
    args = parse_args(argv[1:])
    host = "https://stfc.atlassian.net"
    username = args.username
    password = args.password
    output_location = args.output

    Path(output_location).mkdir(exist_ok=True)

    csv_output_location = path.join(output_location, "JSM Metric Data.csv")
    xlsx_output_location = path.join(output_location, "JSM Metric Spreadsheet.xlsx")

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

    save_csv(jsm_data, csv_output_location)

    generate_xlsx_file(csv_output_location, xlsx_output_location)


if __name__ == '__main__':
    jsm_metric_collection()
