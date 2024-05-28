"""This module handles the Slack Application status notifications."""

from slack_sdk import WebClient
from src.read_data import get_token, get_maintainer


def online_notif() -> None:
    """
    This method sends a message to the maintainer notifying that the application is running.
    :return: True
    """
    maintainer = get_maintainer()
    client = WebClient(token=get_token("SLACK_BOT_TOKEN"))
    client.chat_postMessage(
        channel=maintainer,
        text="Cloud ChatOps is online.",
    )
