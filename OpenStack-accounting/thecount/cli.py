import os
import argparse
import re
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from thecount.sink import Sink
from thecount.source import Source
from thecount.structs import RunDetails
from thecount.jobs import Job, CinderAccounting, GlanceAccounting, NovaAccounting, ManilaAccounting

logger = logging.getLogger(__name__)

# parse jobs
ALL_JOBS: dict[str, type[Job]] = {
    "cinder": CinderAccounting,
    "glance": GlanceAccounting,
    "nova": NovaAccounting,
    "manila": ManilaAccounting
}

def setup_parser() -> argparse.ArgumentParser:
    """
    setup parser rules, to read in and validate command line arguments
    """
    parser = argparse.ArgumentParser(
        prog="thecount",
        description="Extract accounting records from openstack db and send them to the influx.",
        epilog=(
            "Only ISO 8601 time formats are accepted (2024-01-01, 2024-01-01T09:00) "
            "values without timezone are treated as UTC."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--job", action="append", metavar="NAME", default=None,
        help="accounting job to run; repeatable, or comma-separated - see --list-jobs for full list",
    )
    selection.add_argument("--all", action="store_true", help="run every accounting job")

    # default is None as current time calculated at runtime
    parser.add_argument(
        "--start-time", metavar="TIME", default=None,
        help="(optional) start of the range ISO 8601 format( yyyy-mm-ddTHH:MM:SS ), "
             "if not given, --start-time will be set as the current time",
    )
    parser.add_argument(
        "--end-time", metavar="TIME", default=None,
        help="end of the range, if in the future, script will complete once that range is reached"
             " if not given, will run from given --start-time and keep running forever until killed (default: None)"
             " ISO 8601 format( yyyy-mm-ddTHH:MM:SS )",
    )
    parser.add_argument(
        "--interval", metavar="DURATION", default="1440",
        help="size of window (in minutes) for each accounting extraction period - USAGE: 1440, 60, 15 "
             "value must be >=15, default is 1440 (1 day)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="print the records to be sent instead of sending to influxdb",
    )
    parser.add_argument(
        "--config-path", metavar="THE_COUNT_CONFIG_FILE", default=os.environ.get("$THE_COUNT_CONFIG_FILE"),
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


def _as_utc(dt: datetime) -> datetime:
    """
    Helper string to convert datetime to UTC if timezone given
    dt: python datetime object
    :returns: equivalent python datetime object converted to the equivalent UTC timezone time
    """
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt

def build_config(args: argparse.Namespace) -> RunDetails:
    """
    Validates and parses input values and creates a RunDetails dataclass to hold configuration details on
    how to run various accounting jobs
    :params args: argparse Namespace containing args passed in via CLI
    :returns: a RunDetails struct containing parameters on what accounting jobs to run and how to run them
    """

    names = list(ALL_JOBS)
    if not args.all:
        names = _split_jobs(args.jobs)
        if not names:
            raise ValueError("specify --job NAME (repeatable) or --all")
        unknown = [name for name in names if name not in ALL_JOBS]
        if unknown:
            raise ValueError(f"unknown job(s): {', '.join(unknown)}. Available: {ALL_JOBS}")
    requested_jobs = [ALL_JOBS[name]() for name in names]

    # times and durations
    try:
        interval = timedelta(minutes=int(args.interval))
    except ValueError as e:
        raise ValueError(f"malformed interval {args.interval}") from e
    if interval < timedelta(minutes=15):
        raise ValueError(f"interval {args.interval} set at < 15 which is likely to cause DB slowdowns")

    if args.end_time:
        try:
            end = _as_utc(datetime.fromisoformat(args.end_time))
        except ValueError:
            raise ValueError(
                f"unable to parse --end-time {args.end_time}, accepted format ISO 8601'"
            )
    else:
        end = None
        logger.info("--end-time not set, running continuously...")

    if args.start_time:
        try:
            start = _as_utc(datetime.fromisoformat(args.start_time))
        except ValueError:
            raise ValueError(
                f"unable to parse --start-time {args.start_time}, accepted format ISO 8601'"
            )
    else:
        start = datetime.now(timezone.utc)
        logger.info(f"--start-time set to {start}")

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
        interval=interval,
        start_time=start,
        end_time=end,
    )