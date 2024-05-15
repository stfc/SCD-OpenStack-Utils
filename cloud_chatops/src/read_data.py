from typing import List, Dict
import json
from src.custom_exceptions import RepositoriesNotGiven, UserMapNotGiven, TokensNotGiven


def validate_required_files() -> None:
    """
    This function checks that all required files have data in them before the application runs.
    """
    repos = get_repos()
    if not repos:
        raise RepositoriesNotGiven("repos.csv does not contain any repositories.")

    tokens = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "GITHUB_TOKEN", "INFLUX_TOKEN"]
    for token in tokens:
        temp = get_token(token)
        if not temp:
            raise TokensNotGiven(f"Token {token} does not have a value in secrets.json.")
    user_map = get_user_map()
    if not user_map:
        raise UserMapNotGiven("user_map.json is empty.")
    for item, value in user_map.items():
        if not value:
            raise UserMapNotGiven(f"User {item} does not have a Slack ID assigned.")


def get_token(secret: str) -> str:
    """
    This function will read from the secrets file and return a specified secret.
    :param secret: The secret to find
    :return: A secret as string
    """
    with open("./secrets.json", "r", encoding="utf-8") as file:
        data = file.read()
    secrets = json.loads(data)
    return secrets[secret]


def get_repos() -> List[str]:
    """
    This function reads the repo csv file and returns a list of repositories
    :return: List of repositories as strings
    """
    with open("./repos.csv", "r", encoding="utf-8") as file:
        data = file.read()
        repos = data.split(",")
        if not repos[-1]:
            repos = repos[:-1]
    return repos


def get_user_map() -> Dict:
    """
    This function gets the GitHub to Slack username mapping from the map file.
    :return: Dictionary of username mapping
    """
    with open("./user_map.json", "r", encoding="utf-8") as file:
        data = file.read()
        user_map = json.loads(data)
    return user_map


def get_maintainer() -> str:
    """
    This function will get the maintainer user's Slack ID from the text file.
    :return: Slack Member ID or Kalibh Halford if not provided
    """
    with open("./maintainer.txt", "r", encoding="utf-8") as file:
        data = file.read()
        if not data:
            return "U05RBU0RF4J"
        return data
