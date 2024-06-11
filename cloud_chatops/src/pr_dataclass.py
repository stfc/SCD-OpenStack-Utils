"""
This module declares the dataclass used to store PR information.
This is preferred over dictionaries as dataclasses make code more readable.
"""
from dataclasses import dataclass

# Disabling this Pylint error as the dataclass needs to hold more than 7 attributes.
# pylint: disable=R0902
@dataclass
class PrData:
    """Class holding information about a single pull request."""
    pr_title: str
    user: str
    url: str
    created_at: str
    channel: str
    thread_ts: str
    mention: bool
    draft: bool
    old: bool = False
