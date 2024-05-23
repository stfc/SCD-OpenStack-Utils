import logging
import asyncio
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
import schedule
from src.pr_reminder import PostPRsToSlack
from src.read_data import get_token, validate_required_files
from src.post_to_influx import PostDataToInflux
from src.online_notif import online_notif


logging.basicConfig(level=logging.DEBUG)
app = AsyncApp(token=get_token("SLACK_BOT_TOKEN"))


@app.command("/prs")
async def remind_prs(ack, respond, command):
    """
    This function calls the messaging method to notify a user about their open PRs or all open PRs if asked.
    :param command: The return object from Slack API.
    :param ack: Slacks acknowledgement command.
    :param respond: Slacks respond command to respond to the command in chat.
    """
    await ack()
    await respond("Gathering the PRs...")

    channel = command["user_id"]
    if command['text'] == 'mine':
        PostPRsToSlack().run_private(channel=channel)
    elif command['text'] == 'all':
        PostPRsToSlack().run_public(mention=False, channel=channel)
    else:
        await respond("Please provide the correct argument: 'mine' or 'all'.")
        return

    await respond("Check out your DMs.")


async def schedule_jobs() -> None:
    """
    This function schedules tasks for the async loop to run when the time is right.
    """

    def run_pr(channel, mention=False):
        """
        This is a placeholder function for the schedule to accept.
        """
        PostPRsToSlack().run_public(mention=mention, channel=channel)

    def post_data():
        """
        This is a placeholder function for the schedule to accept.
        """
        PostDataToInflux().run()

    schedule.every().monday.at("09:00").do(
        run_pr, mention=True, channel="pull-requests"
    )
    schedule.every().wednesday.at("09:00").do(run_pr, channel="pull-requests")
    schedule.every().friday.at("09:00").do(run_pr, channel="pull-requests")

    schedule.every().day.at("09:00").do(post_data)

    assert online_notif()
    while True:
        schedule.run_pending()
        await asyncio.sleep(10)


async def main() -> None:
    """
    This function is the main entry point for the application. First, it validates the required files.
    Then it starts the async loop and runs the scheduler.
    """
    validate_required_files()
    asyncio.ensure_future(schedule_jobs())
    handler = AsyncSocketModeHandler(app, get_token("SLACK_APP_TOKEN"))
    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
