from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
from sys import argv
from time import sleep
from os import path
from wordcloud import WordCloud
from typing import Optional, Dict, List
from dataclasses import dataclass
from mashumaro import DataClassDictMixin
import re
import json
import requests


@dataclass
class IssuesFilter(DataClassDictMixin):
    output: str
    start_date: str
    end_date: str
    word_cloud: str
    assigned: Optional[str] = None
    filter_for: Optional[str] = None
    filter_not: Optional[str] = None


def from_user_inputs(**kwargs):
    """
    Take the inputs from an argparse and populate a IssuesFilter dataclass and return it
    :param kwargs: a dictionary of argparse values
    """

    return IssuesFilter(**kwargs)


def parse_args(inp_args: Dict) -> Dict:
    """
    Function to parse commandline args
    :param inp_args: a set of commandline args to parse
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
    default_value_start_date = datetime.now().strftime("%Y-%m-%d")
    parser.add_argument(
        "-s",
        "--start_date",
        metavar="START_DATE",
        help="Date to get issues from",
        default=default_value_start_date,
    )
    default_value_end_date = (datetime.now() - relativedelta(months=1)).strftime(
        "%Y-%m-%d"
    )
    parser.add_argument(
        "-e",
        "--end_date",
        metavar="END_DATE",
        help="Date to get issues to",
        default=default_value_end_date,
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
    parser.add_argument(
        "-w",
        "--word_cloud",
        metavar="WORD_CLOUD",
        help="Parameters to create the word cloud with",
        default="2000, 1000, 25, 10000",
    )
    args = parser.parse_args(inp_args)
    return args


def get_response_json(auth, headers: Dict, url: str) -> Dict:
    """
    Function to send a get request to a url and return the response as json
    :param auth: A HTTPBasicAuth object for authentication (HTTPBasicAuth)
    :param headers: A request Header
    :param url: The URL to send the request
    :returns: A dictionary of JSON values
    """
    session = requests.session()
    session.headers = headers
    session.auth = auth

    attempts = 5
    response = None

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


def get_issues_contents_after_time(
    auth, headers: Dict, host: str, issue_filter: Dict
) -> List:
    """
    Function to get the contents of through issues using a loop, as only 50 can be checked at a time
    :param issue_filter: Dict of filters to check the issues against
    :param auth: A HTTPBasicAuth object for authentication (HTTPBasicAuth)
    :param headers: A request Header
    :param host: The host used to create the URL to send the request
    :returns: A list with the contents of all valid issues
    """
    curr_marker = 0
    check_limit = 50
    issues_contents = []
    while True:
        url = f"{host}/rest/servicedeskapi/servicedesk/6/queue/182/issue?start={curr_marker}"
        json_load = get_response_json(auth, headers, url)
        issues = json_load.get("values")
        issues_length = json_load.get("size")
        for i, issue in enumerate(issues, 1):
            issue_date = datetime.strptime(
                issue.get("fields").get("created")[:10], "%Y-%m-%d"
            )
            if issue_date < datetime.strptime(issue_filter.end_date, "%Y-%m-%d"):
                return issues_contents
            if filter_issue(issue, issue_filter, issue_date):
                issue_contents = issue.get("fields").get("summary")
                if issue_contents:
                    issues_contents.append(issue_contents)

        # break out of the loop if we reach the end of the issue list
        if issues_length < check_limit:
            break
        curr_marker += issues_length
    return issues_contents


def filter_issue(issue: Dict, issue_filter: Dict, issue_date: str) -> bool:
    """
    Function to check if an issue passes the set filters
    :param issue: A dict of an issues contents
    :param issue_filter: Dict of filters to check the issues against
    :param issue_date: The date that the issue was created
    :returns: If the issue passes the filters
    """
    fields = issue.get("fields", None)
    if not fields:
        return False

    assignee = fields.get("assignee", None)
    if not assignee:
        return False

    issue_assigned = assignee.get("displayName", None)
    assign_check = issue_filter.assigned
    if (not issue_assigned or issue_assigned != assign_check) and assign_check:
        return False

    if issue_date > datetime.strptime(issue_filter.start_date, "%Y-%m-%d"):
        return False
    return True


def generate_word_cloud(
    issues_contents: List, issue_filter: Dict, word_cloud_output_location, **kwargs
):
    """
    Function to generate and save a word cloud
    :param issues_contents: The summary of every valid issue
    :param issue_filter: Dict of filters to check the issues against
    :param word_cloud_output_location: The output location for the word cloud to be saved to
    :param kwargs: A set of kwargs to pass to WordCloud
    - width
    - height
    - min_font_size
    - max_words
    """
    matches = re.findall(r"((\w+([.'](?![ \n']))*[-_]*)+)", issues_contents)
    # Regex to find all words and include words joined with certain characters, while not
    # allowing certain characters to exist at the start or end of the word, such as dots.
    if matches:
        issues_contents = " ".join(list(list(zip(*matches))[0]))
    issues_contents = filter_word_cloud(issue_filter, issues_contents)
    word_cloud = WordCloud(
        width=kwargs["width"],
        height=kwargs["height"],
        min_font_size=kwargs["min_font_size"],
        max_words=kwargs["max_words"],
        background_color="white",
        collocations=False,
        regexp=r"\w*\S*",
    )

    word_cloud.generate(issues_contents)

    word_cloud.to_file(word_cloud_output_location)


def filter_word_cloud(issue_filter: Dict, issues_contents: List):
    """
    Function to filter the contents of the word cloud to or against certain strings
    :param issues_contents: The summary of every valid issue
    :param issue_filter: Dict of filters to check the issues against
    :returns: The filtered issues contents
    """
    if issue_filter.filter_not:
        issues_contents = re.sub(
            issue_filter.filter_not.lower(), "", issues_contents, flags=re.I
        )
    if issue_filter.filter_for:
        issues_contents = " ".join(
            re.findall(
                issue_filter.filter_for.lower(),
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

    issue_filter = from_user_inputs(vars(args))

    parameters_list = issue_filter.word_cloud.split(", ")
    word_cloud_parameters = {
        "width": int(parameters_list[0]),
        "height": int(parameters_list[1]),
        "min_font_size": int(parameters_list[2]),
        "max_words": int(parameters_list[3]),
    }

    Path(issue_filter.output).mkdir(exist_ok=True)

    word_cloud_output_location = path.join(
        issue_filter.output,
        f"word cloud - {datetime.now().strftime('%Y.%m.%d.%H.%M.%S')}.png",
    )

    auth = requests.auth.HTTPBasicAuth(username, password)
    headers = {
        "Accept": "application/json",
    }

    issues_contents = get_issues_contents_after_time(auth, headers, host, issue_filter)

    generate_word_cloud(
        " ".join(issues_contents),
        issue_filter,
        word_cloud_output_location,
        **word_cloud_parameters,
    )


if __name__ == "__main__":
    word_cloud_generator()
