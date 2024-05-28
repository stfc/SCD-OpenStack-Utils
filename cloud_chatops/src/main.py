"""
This module is the entry point to the Slack Application.
It can be run here as the entry point or use the main method.
"""

import asyncio
from src.slack_app import run_app


def main():
    """This method is the entry point if using this package."""
    asyncio.run(run_app())


if __name__ == "__main__":
    asyncio.run(run_app())
