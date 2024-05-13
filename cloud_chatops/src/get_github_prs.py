from typing import List, Dict, Union
from src.read_data import get_token
import requests


class RepoNotFound(Exception):
    """This class creates a custom Exception, so we don't raise "broad" exceptions."""

    pass


class UnknownHTTPError(Exception):
    """This class creates a custom Exception, so we don't raise "broad" exceptions."""

    pass


class GetGitHubPRs:
    """
    This class handles getting the open PRs from the GitHub Rest API.
    """

    def __init__(self, repos: List):
        self.repos = repos

    def run(self) -> Dict[str, List]:
        unformatted_responses = self.request_all_repos_http()
        formatted_responses = self.format_http_responses(unformatted_responses)
        return formatted_responses

    def request_all_repos_http(self) -> Dict[str, List[Dict]]:
        """
        This method starts a request for each repository and returns a list of those PRs.
        :return: A list of PRs
        """
        responses = {}
        for repo in self.repos:
            url = f"https://api.github.com/repos/stfc/{repo}/pulls"
            response = self.get_http_response(url)
            responses[repo] = response
        return responses

    @staticmethod
    def get_http_response(url: str) -> List[Dict]:
        """
        This method sends a HTTP request to the GitHub Rest API endpoint and returns all open PRs from that repository.
        :param url: The URL to make the request to
        :return: The response in JSON form
        """
        headers = {"Authorization": "token " + get_token("GITHUB_TOKEN")}
        response = requests.get(url, headers=headers, timeout=60)
        return response.json()

    @staticmethod
    def format_http_responses(
        responses: Union[Dict[str, List], Dict[str, Dict]]
    ) -> Dict[str, List]:
        """
        This method checks if the response returned a list of PRs (where a single repo has multiple PRs)
        or if a response returned a single PR (where a single repo has one PR). Then returns them in a list.
        :param responses: GitHub's responses of a list of PRs or single PR
        :return: The PRs all in the same structure.
        """
        to_remove = []
        for repo, response in responses.items():
            if isinstance(response, dict) and len(response) == 2:
                raise RepoNotFound(f'The repo "{repo}" could not be found.')
            elif isinstance(response, list) and not response:
                to_remove.append(repo)
            elif isinstance(response, list) and response:
                pass
            else:
                raise UnknownHTTPError(
                    f"An unexpected HTTP response was found: {response}\n"
                )
        for i in to_remove:
            del responses[i]
        return responses
