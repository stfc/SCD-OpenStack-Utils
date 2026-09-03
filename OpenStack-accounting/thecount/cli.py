import os
import argparse
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from thecount.sink import Sink
from thecount.source import Source
from thecount.structs import RunDetails

from thecount.parsers.base_parser import BaseParser
from thecount.parsers.glance_parser import GlanceParser
from thecount.parsers.cinder_parser import CinderParser
from thecount.parsers.manila_parser import ManilaParser
from thecount.parsers.nova_parser import NovaParser

logger = logging.getLogger(__name__)

# hardcoded interval
INTERVAL_HOURS = timedelta(hours=24)

# parse jobs
ALL_JOBS: dict[str, type[BaseParser]] = {
    "cinder": CinderParser,
    "glance": GlanceParser,
    "nova": NovaParser,
    "manila": ManilaParser,
}

def setup_parser() -> argparse.ArgumentParser:
    """
    setup parser rules, to read in and validate command line arguments
    """
    parser = argparse.ArgumentParser(
        prog="thecount",
        description="Extract accounting records from openstack db and send them to the influx.",
        epilog=(
            "Only yyyy-mm-dd time formats are accepted (e.g. 2024-01-01) "
            "timezone is always treated as UTC."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--job",
        action="append",
        metavar="NAME",
        default=None,
        help="accounting job to run; repeatable, or comma-separated - see --list-jobs for full list",
    )
    parser.add_argument(
        "--all", action="store_true", default=False, help="run every accounting job"
    )

    # default is None as current time calculated at runtime
    parser.add_argument(
        "--start-time",
        metavar="TIME",
        default=None,
        help="(optional) start of the range in format: yyyy-mm-dd"
        "if not given, --start-time will be set as midnight the day before current date",
    )
    parser.add_argument(
        "--end-time",
        metavar="TIME",
        default=None,
        help="end of the range, if in the future, script will complete once that range is reached"
        " if not given, will run from given --start-time and keep running forever until killed (default: None)"
        " format yyyy-mm-dd",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the records to be sent instead of sending to influxdb",
    )
    parser.add_argument(
        "--config-path",
        metavar="THE_COUNT_CONFIG_FILE",
        default=os.environ.get("THE_COUNT_CONFIG_FILE"),
        help="config file with source and sink credentials (default: $THE_COUNT_CONFIG_FILE)",
    )
    return parser


def _split_jobs(values: Optional[List[str]]) -> list[str]:
    """
    Helper function that splits comma-spaced job names into a list of distinct jobs to run
    global mapping of name to job class is specified in ALL_JOBS const variable at the top
    of this file
    :param values: comma-spaced list of job names
    :return: list of distinct job classes corresponding to given job nmaes
    """
    if not values:
        return []

    names: list[str] = []
    for value in values:
        parts = [part.strip() for part in value.split(",") if part.strip()]
        names.extend(parts)
    # removes duplicates whilst preserving order
    return list(dict.fromkeys(names))


def _parse_date(value: str) -> datetime:
    """
    Helper string to convert yyyy-mm-dd string into UTC datetime
    value: string to represent date in format yyyy-mm-dd
    :returns: equivalent python datetime object with UTC timezone info
    """
    try:
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError as e:
        raise ValueError(f"unable to parse {value}, accepted format YYYY-MM-DD") from e


def build_config(args: argparse.Namespace) -> RunDetails:
    """
    Validates and parses input values and creates a RunDetails dataclass to hold configuration details on
    how to run various accounting jobs
    :params args: argparse Namespace containing args passed in via CLI
    :returns: a RunDetails struct containing parameters on what accounting jobs to run and how to run them
    """

    if args.all and args.job:
        raise ValueError("--all cannot be used with --job")

    # defaults to --all if neither given - i.e. run all jobs in list
    names = list(ALL_JOBS)

    # if --job specified, parse input and validate
    if args.job:
        names = _split_jobs(args.job)
        unknown = [name for name in names if name not in ALL_JOBS]
        if unknown:
            raise ValueError(
                f"unknown job(s): {', '.join(unknown)}. Available: {ALL_JOBS}"
            )

    requested_jobs = [ALL_JOBS[name]() for name in names]

    # parse times
    try:
        end = _parse_date(args.end_time) if args.end_time else None
    except ValueError as e:
        raise ValueError(f"unable to parse --end-time: {e}") from e
    if end is None:
        logger.info("--end-time not set, running continuously...")

    if args.start_time:
        try:
            start = _parse_date(args.start_time)
        except ValueError as e:
            raise ValueError(f"unable to parse --start-time: {e}") from e
    else:
        today = datetime.now(timezone.utc).date()
        curr = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
        start = curr - timedelta(days=1)
        logger.info("--start-time set to %s (yesterday)", start)

    # if --end-time given, make sure it is after --start-time (or current date if not given)
    if end and start >= end:
        raise ValueError(
            f"--start-time ({start.isoformat()}) must be before "
            f"--end-time ({end.isoformat()})"
        )

    return RunDetails(
        jobs=requested_jobs,
        sink=Sink(args.config_path),
        source=Source(args.config_path),
        dry_run=args.dry_run,
        interval=INTERVAL_HOURS,
        start_time=start,
        end_time=end,
    )
