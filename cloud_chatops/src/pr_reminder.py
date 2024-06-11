"""This module handles the posting of messages to Slack using the Slack SDK WebClient class."""

from typing import List
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from read_data import get_token, get_user_map, get_repos
from get_github_prs import GetGitHubPRs
from pr_dataclass import PrData


class PostPRsToSlack:
    """
    This class handles the Slack posting.
    """

    def __init__(self):
        super().__init__()
        self.repos = get_repos()
        self.client = WebClient(token=get_token("SLACK_BOT_TOKEN"))
        self.slack_ids = get_user_map()
        self.prs = GetGitHubPRs(get_repos(), "stfc").run()
        self.channel = "temp-chatops"

    def run(self, mention, channel=None) -> None:
        """
        This method calls the functions to post the reminder message and subsequent PR messages.
        :param channel: Changes the channel to post the messages to.
        :param mention: To mention the users in Slack or just post their name.
        """
        if channel:
            self.channel = channel
        reminder_message = self.post_reminder_message()
        self.post_thread_messages(self.prs, reminder_message, mention)

    def post_reminder_message(self) -> WebClient.chat_postMessage:
        """
        This method posts the main reminder message to start the thread if PR notifications.
        :return: The reminder message return object
        """
        reminder = self.client.chat_postMessage(
            channel=self.channel,
            text="Here are the outstanding PRs as of today:",
        )
        return reminder

    def post_thread_messages(
        self,
        prs: Dict[str, List],
        reminder_message: WebClient.chat_postMessage,
        mention: bool,
    ) -> None:
        """
        This method iterates through each PR and calls the post method for them.
        :param mention: To mention the users or not
        :param prs: A list of PRs from GitHub
        :param reminder_message: The reminder message object
        """
        prs_found = False
        for repo in prs.values():
            for pr in repo:
                info = PrData(
                    pr_title=f"{pr['title']} #{pr['number']}",
                    user=pr["user"]["login"],
                    url=pr["html_url"],
                    created_at=pr["created_at"],
                    channel=reminder_message.data["channel"],
                    thread_ts=reminder_message.data["ts"],
                    mention=mention,
                    draft=pr["draft"],
                )
                prs_found = True
                checked_info = self.check_pr(info)
                self.send_thread(checked_info)

        if not prs_found:
            self.send_no_prs(reminder_message)

    def send_no_prs(self, reminder: WebClient.chat_postMessage) -> None:
        """
        This method sends a message to the user that they have no PRs open.
        This method is only called if no other PRs have been mentioned.
        :param reminder: The thread message to send under.
        """
        self.client.chat_postMessage(
            text="There are no outstanding pull requests open.",
            channel=reminder.data["channel"],
            thread_ts=reminder.data["ts"],
            unfurl_links=False,
        )

    def check_pr(self, info: PrData) -> PrData:
        """
        This method validates certain information in the PR data such as who authored the PR and if it's old or not.
        :param info: The information to validate.
        :return: The validated information.
        """
        if info.user not in self.slack_ids:
            # If the PR author is not in the Slack ID mapping
            # then we set the user to mention as David Fairbrother
            # as the team lead to deal with this PR.
            info.user = "U01JG0LKU3W"
        else:
            info.user = self.github_to_slack_username(info.user)
        opened_date = datetime.fromisoformat(info.created_at).replace(tzinfo=None)
        datetime_now = datetime.now().replace(tzinfo=None)
        time_cutoff = datetime_now - timedelta(days=30 * 6)
        if opened_date < time_cutoff:
            info.old = True
        del info.created_at
        return info

    def send_thread(
        self,
        data: PrData
    ) -> None:
        """
        This method sends the thread message and prepares the reactions.
        :param data: The PR data as a dataclass
        """
        message = self.construct_message(data.pr_title, data.user, data.url, data.mention, data.draft, data.old)
        response = self.client.chat_postMessage(
            text=message, channel=data.channel, thread_ts=data.thread_ts, unfurl_links=False
        )
        assert response["ok"]
        reactions = {
            "old": data.old,
            "draft": data.draft,
        }
        self.send_thread_react(data.channel, response.data["ts"], reactions)

    def send_thread_react(self, channel: str, ts: str, reactions: Dict) -> None:
        """
        This method sends reactions to the PR message if necessary.
        """
        mapping = {
            "old": "alarm_clock",
            "draft": "scroll",
        }
        for react in reactions:
            if reactions[react]:
                react_response = self.client.reactions_add(
                    channel=channel, name=mapping[react], timestamp=ts
                )
                assert react_response["ok"]

    def construct_message(
        self, pr_title: str, user: str, url: str, mention: bool, draft: bool, old: bool
    ) -> str:
        """
        This method constructs the PR message depending on if the PR is old and if the message should mention or not.
        :param pr_title: The title of the PR.
        :param user: The author of the PR.
        :param url: The URL of the PR.
        :param mention: To mention users or not.
        :param draft: If the PR is a draft.
        :param old: If the PR is older than 6 months.
        :return:
        """
        message = []
        if old:
            message.append("*This PR is older than 6 months. Consider closing it:*")
        message.append(f"Pull Request: <{url}|{pr_title}>")
        if mention and not draft:
            message.append(f"Author: <@{user}>")
        else:
            name = self.get_real_name(user)
            message.append(f"Author: {name}")

        return "\n".join(message)

    def get_real_name(self, username: str) -> str:
        """
        This method uses the Slack client method to get the real name of a user and returns it.
        :param username: The user ID to look for
        :return: Returns the real name or if not found the name originally parsed in
        """
        try:
            name = self.client.users_profile_get(user=username)["profile"]["real_name"]
        except SlackApiError:
            name = username
        return name

    def github_to_slack_username(self, user: str) -> str:
        """
        This method checks if we have a Slack id for the GitHub user and returns it.
        :param user: GitHub username to check for
        :return: Slack ID or GitHub username
        """
        if user in self.slack_ids:
            return self.slack_ids[user]
        return user
