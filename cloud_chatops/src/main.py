"""
This module is the entry point to the Slack Application.
It can be run here as the entry point or use the main method.
"""

from slack_app import run_app
import asyncio


def main():
    """This method is the entry point if using this package."""
    asyncio.run(run_app())


if __name__ == "__main__":
    """This method is the entry point if using this file."""
    asyncio.run(run_app())
