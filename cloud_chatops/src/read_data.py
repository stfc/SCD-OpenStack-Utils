from typing import List, Dict
import json


def get_token(secret: str) -> str:
    """
    This method will read from the secrets file and return a specified secret.
    :param secret: The secret to find
    :return: A secret as string
    """
    with open("./secrets.json", "r", encoding="utf-8") as file:
        data = file.read()
    secrets = json.loads(data)
    return secrets[secret]


def get_repos() -> List[str]:
    """
    # Note: CSV file must end in ",".
    This method reads the repo csv file and returns a list of repositories
    :return: List of repositories as strings
    """
    with open("./repos.csv", "r", encoding="utf-8") as file:
        data = file.read()
        repos = data.split(",")
        repos = repos[:-1]
    return repos


def get_user_map() -> Dict:
    """
    This method gets the GitHub to Slack username mapping from the map file.
    :return: Dictionary of username mapping
    """
    with open("./user_map.json", "r", encoding="utf-8") as file:
        data = file.read()
        user_map = json.loads(data)
    return user_map
