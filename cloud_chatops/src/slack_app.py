"""
This module starts the Slack Bolt application Asynchronously running the event loop.
Using Socket Mode the application listens for events from the Slack API client.
Slash commands are also defined here.
"""

import logging
import asyncio
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
import schedule
from src.pr_reminder import PostPRsToSlack
from src.read_data import get_token, validate_required_files
from src.online_notif import online_notif


logging.basicConfig(level=logging.DEBUG)
app = AsyncApp(token=get_token("SLACK_BOT_TOKEN"))


async def schedule_jobs() -> None:
    """
    This function schedules tasks for the async loop to run when the time is right.
    """

    def run_pr(channel, mention=False):
        """
        This is a placeholder function for the schedule to accept.
        """
        PostPRsToSlack().run(mention=mention, channel=channel)

    schedule.every().monday.at("09:00").do(
        run_pr, mention=True, channel="pull-requests"
    )
    schedule.every().wednesday.at("09:00").do(run_pr, channel="pull-requests")
    schedule.every().friday.at("09:00").do(run_pr, channel="pull-requests")

    online_notif()
    while True:
        schedule.run_pending()
        await asyncio.sleep(10)


async def run_app() -> None:
    """
    This function is the main entry point for the application. First, it validates the required files.
    Then it starts the async loop and runs the scheduler.
    """
    validate_required_files()
    asyncio.ensure_future(schedule_jobs())
    handler = AsyncSocketModeHandler(app, get_token("SLACK_APP_TOKEN"))
    await handler.start_async()
