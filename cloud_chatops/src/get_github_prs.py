"""
This module handles the HTTP requests and formatting to the GitHub REST Api.
It will get all open pull requests in provided STFC owned repositories.
"""

from typing import List, Dict, Union
from src.read_data import get_token
from src.custom_exceptions import RepoNotFound, UnknownHTTPError, BadGitHubToken
import requests


class GetGitHubPRs:
    """
    This class handles getting the open PRs from the GitHub Rest API.
    """

    def __init__(self, repos: List[str], owner: str):
        """
        This method initialises the class with the following attributes to be edited and accessed through the run method.
        :param repos: A list of repositories to get pull requests for.
        :param repos: The owner of the above repositories.
        """
        self.repos = repos
        self.owner = owner

    def run(self) -> Dict[str, List]:
        """
        This method is the entry point to the class.
        It runs the HTTP request methods and the formatting methods.
        :return: The responses from the HTTP requests.
        """
        unformatted_responses = self.request_all_repos_http()
        formatted_responses = self.format_http_responses(unformatted_responses)
        return formatted_responses

    def request_all_repos_http(self) -> Dict[str, List[Dict]]:
        """
        This method starts a request for each repository and returns a list of those PRs.
        :return: A dictionary of repos and their PRs.
        """
        responses = {}
        for repo in self.repos:
            url = f"https://api.github.com/repos/{self.owner}/{repo}/pulls"
            response = self.get_http_response(url)
            responses[repo] = response
        return responses

    def get_http_response(self, url: str) -> List[Dict]:
        """
        This method sends a HTTP request to the GitHub Rest API endpoint and returns all open PRs from that repository.
        :param url: The URL to make the request to
        :return: The response in JSON form
        """
        headers = {"Authorization": "token " + get_token("GITHUB_TOKEN")}
        response = requests.get(url, headers=headers, timeout=60)
        self.validate_response(response, url)
        return response.json()

    def format_http_responses(
        self, responses: Union[Dict[str, List], Dict[str, Dict]]
    ) -> Dict[str, List]:
        """
        This method checks the formats the responses from GitHub are in a consistent format.
        :param responses: GitHub's HTTP responses.
        :return: Dictionary of responses.
        """
        culled_responses = self.remove_empty_response(responses)
        for repo, response in culled_responses.items():
            if isinstance(response, dict):
                responses[repo] = [response]
        return responses

    @staticmethod
    def remove_empty_response(
        responses: Union[Dict[str, List], Dict[str, Dict]]
    ) -> Union[Dict[str, List], Dict[str, Dict]]:
        """
        This method removes all empty responses from the Dictionary.
        An empty response is the result of no open pull requests.
        :param responses: The responses to check.
        :return: The responses with no empty values.
        """
        to_remove = []
        for repo, response in responses.items():
            if not response:
                to_remove.append(repo)

        for i in to_remove:
            del responses[i]
        return responses

    @staticmethod
    def validate_response(response: requests.get, url: str) -> None:
        """
        This method checks the status code of the HTTP response and handles exceptions accordingly.
        :param response: The response to check.
        :param url: The url that was not found.
        """
        if response.status_code == 401:
            raise BadGitHubToken(
                "Your GitHub api token is invalid. Check that it hasn't expired."
            )
        if response.status_code == 404:
            raise RepoNotFound(f'The repo at the url "{url}" could not be found.')

        if response.status_code != 200:
            raise UnknownHTTPError(
                f'The HTTP response code is unknown and cannot be handled. Response: {response.status_code}'
            )
