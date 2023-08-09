from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
from sys import argv
from time import sleep
from os import path
from wordcloud import WordCloud

import json
import matplotlib.pyplot as pyplot
import requests
import re


def parse_args(inp_args):
    """
    Function to parse commandline args
    :param inp_args: a set of commandline args to parse (dict)
    :returns: A dictionary of parsed args
    """
    # Get arguments passed to the script
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)

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
    parser.add_argument(
        "-d",
        "--date",
        metavar="Date",
        help="Date to get issues since",
        default=datetime.now() - relativedelta(months=1),
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
        if (
                response.content != b'{"status":"RUNNING"}'
                and response.content != b'{"status":"ENQUEUED"}'
        ):
            break
        else:
            sleep(1)
            attempts = attempts - 1

    if attempts == 0:
        raise requests.exceptions.Timeout(
            "Get request status not completed before timeout"
        )

    return json.loads(response.text)


def get_issues_contents_after_time(auth, headers, host, date):
    """
    Function to get the number of issues using a loop, as only 50 can be checked at a time
    :param date: Time to get issues since (datetime.datetime)
    :param auth: A HTTPBasicAuth object for authentication (HTTPBasicAuth)
    :param headers: A request Header (dict)
    :param host: The host used to create the URL to send the request (string)
    :returns: A list with only a string containing the number of issues
    """
    issues_contents = []
    return_amount = 50
    issues_amount = 0
    while return_amount == 50:
        url = f"{host}/rest/servicedeskapi/servicedesk/6/queue/182/issue?start={issues_amount}"

        json_load = get_response_json(auth, headers, url)

        issues = json_load.get("values")

        for issue in issues:
            issue_date = datetime.strptime(issue.get("fields").get("created")[:10], "%Y-%m-%d")
            if issue_date < date:
                return issues_contents
            issue_contents = issue.get("fields").get("summary")
            if issue_contents:
                issues_contents.append(issue_contents)

        return_amount = json_load.get("size")
        issues_amount = issues_amount + return_amount

    return issues_contents


def generate_word_cloud(issues_contents):
    matches = re.findall(r"((\w+([.'](?![ \n']))*[-_]*)+)", issues_contents)
    issues_contents = " ".join(list(list(zip(*matches))[0]))
    word_cloud = WordCloud(
        width=2000,
        height=1000,
        min_font_size=25,
        max_words=10000,
        background_color="white",
        collocations=False,
        regexp=r"\w*\S*",
    ).generate(issues_contents)

    pyplot.imshow(word_cloud, interpolation="bilinear")
    pyplot.axis("off")
    pyplot.show()


def word_cloud_generator():
    args = parse_args(argv[1:])
    host = "https://stfc.atlassian.net"
    username = args.username
    password = args.password
    output_location = args.output
    date = args.date

    Path(output_location).mkdir(exist_ok=True)

    word_cloud_output_location = path.join(output_location, "JSM Metric Data.csv")

    auth = requests.auth.HTTPBasicAuth(username, password)
    headers = {
        "Accept": "application/json",
    }

    issues_contents = get_issues_contents_after_time(auth, headers, host, date)

    generate_word_cloud(" ".join(issues_contents))


if __name__ == "__main__":
    word_cloud_generator()
