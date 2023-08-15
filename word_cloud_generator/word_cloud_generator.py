from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
from sys import argv
from time import sleep
from os import path
from wordcloud import WordCloud

import json
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
        "-s",
        "--start_date",
        metavar="START_DATE",
        help="Date to get issues from",
        default=datetime.now().strftime("%Y-%m-%d"),
    )
    parser.add_argument(
        "-e",
        "--end_date",
        metavar="END_DATE",
        help="Date to get issues to",
        default=(datetime.now() - relativedelta(months=1)).strftime("%Y-%m-%d"),
    )
    parser.add_argument(
        "-a",
        "--assigned",
        metavar="ASSIGNED",
        help="Assigned user to get tickets from",
    )
    parser.add_argument(
        "-f",
        "--filter_for",
        metavar="FILTER_FOR",
        help="Strings to filter the word cloud for",
    )
    parser.add_argument(
        "-n",
        "--filter_not",
        metavar="FILTER_NOT",
        help="Strings to filter the word cloud to not have",
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


def get_issues_contents_after_time(auth, headers, host, issue_filter):
    """
    Function to get the contents of through issues using a loop, as only 50 can be checked at a time
    :param issue_filter: Dict of filters to check the issues against (dict)
    :param auth: A HTTPBasicAuth object for authentication (HTTPBasicAuth)
    :param headers: A request Header (dict)
    :param host: The host used to create the URL to send the request (string)
    :returns: A list with the contents of all valid issues
    """
    issues_contents = []
    return_amount = 50
    issues_amount = 0
    while return_amount == 50:
        url = f"{host}/rest/servicedeskapi/servicedesk/6/queue/182/issue?start={issues_amount}"

        json_load = get_response_json(auth, headers, url)

        issues = json_load.get("values")

        for issue in issues:
            issue_date = datetime.strptime(
                issue.get("fields").get("created")[:10], "%Y-%m-%d"
            )
            if issue_date < datetime.strptime(issue_filter.get("end_date"), "%Y-%m-%d"):
                return issues_contents
            if filter_issue(issue, issue_filter, issue_date):
                issue_contents = issue.get("fields").get("summary")
                if issue_contents:
                    issues_contents.append(issue_contents)

        return_amount = json_load.get("size")
        issues_amount = issues_amount + return_amount

    return issues_contents


def filter_issue(issue, issue_filter, issue_date):
    """
    Function to check if an issue passes the set filters
    :param issue: A dict of an issues contents (dict)
    :param issue_filter: Dict of filters to check the issues against (dict)
    :param issue_date: The date that the issue was created (string)
    :returns: If the issue passes the filters
    """
    if issue.get("fields").get("assignee"):
        issue_assigned = issue.get("fields").get("assignee").get("displayName")
        if issue_filter.get("assigned") and issue_assigned != issue_filter.get(
            "assigned"
        ):
            return False
    else:
        return False
    if issue_date > datetime.strptime(issue_filter.get("start_date"), "%Y-%m-%d"):
        return False
    return True


def generate_word_cloud(issues_contents, issue_filter, word_cloud_output_location):
    """
    Function to generate and save a word cloud
    :param issues_contents: The summary of every valid issue (list)
    :param issue_filter: Dict of filters to check the issues against (dict)
    :param word_cloud_output_location: The output location for the word cloud to be saved to
    """
    matches = re.findall(r"((\w+([.'](?![ \n']))*[-_]*)+)", issues_contents)
    if matches:
        issues_contents = " ".join(list(list(zip(*matches))[0]))
    issues_contents = filter_word_cloud(issue_filter, issues_contents)
    word_cloud = WordCloud(
        width=2000,
        height=1000,
        min_font_size=25,
        max_words=10000,
        background_color="white",
        collocations=False,
        regexp=r"\w*\S*",
    )

    word_cloud.generate(issues_contents)

    word_cloud.to_file(word_cloud_output_location)


def filter_word_cloud(issue_filter, issues_contents):
    """
    Function to filter the contents of the word cloud to or against certain strings
    :param issues_contents: The summary of every valid issue (list)
    :param issue_filter: Dict of filters to check the issues against (dict)
    :returns: The filtered issues contents
    """
    if issue_filter.get("filter_not"):
        issues_contents = re.sub(
            issue_filter.get("filter_not").lower(), "", issues_contents, flags=re.I
        )
    if issue_filter.get("filter_for"):
        issues_contents = " ".join(
            re.findall(
                issue_filter.get("filter_for").lower(),
                issues_contents,
                flags=re.IGNORECASE,
            )
        )

    return issues_contents


def word_cloud_generator():
    """
    Function to take arguments, generate the output location and run the
    functions to the data for the word cloud and generate it
    """
    args = parse_args(argv[1:])
    host = "https://stfc.atlassian.net"
    username = args.username
    password = args.password
    issue_filter = {}
    for arg in args.__dict__:
        if args.__dict__[arg] is not None and arg != "username" and arg != "password":
            issue_filter.update({arg: args.__dict__[arg]})

    Path(issue_filter.get("output")).mkdir(exist_ok=True)

    word_cloud_output_location = path.join(
        issue_filter["output"],
        f"word cloud - {datetime.now().strftime('%Y.%m.%d.%H.%M.%S')}.png",
    )

    auth = requests.auth.HTTPBasicAuth(username, password)
    headers = {
        "Accept": "application/json",
    }

    issues_contents = get_issues_contents_after_time(auth, headers, host, issue_filter)

    generate_word_cloud(
        " ".join(issues_contents), issue_filter, word_cloud_output_location
    )


if __name__ == "__main__":
    word_cloud_generator()