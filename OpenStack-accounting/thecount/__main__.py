import sys
import time
import logging
from datetime import datetime

from thecount.cli import setup_parser, build_config
from thecount.structs import RunDetails

logger = logging.getLogger(__name__)

def run_jobs(details: RunDetails) -> None:
    with details.source, details.sink:
        step_counter = 0
        current_time = details.start_time
        while True:
            step_counter += 1
            interval_end = current_time + details.interval

            # If there isn't a complete interval before end_time, stop.
            if details.end_time is not None and interval_end > details.end_time:
                logger.info(
                    f" {details.end_time} reached stopping..."
                )
                break

            logger.info(
                f"Starting Loop: {step_counter}: interval_start_time: {current_time}, interval_end_time: {interval_end}"
            )

            # Don't start the process until end of the current interval - so all data is available
            now = datetime.now(current_time.tzinfo)
            if interval_end > now:
                logger.info(f"waiting until {interval_end.isoformat()}...")
                time.sleep((interval_end - now).total_seconds())

            # Run every job for this interval.
            for job in details.jobs:
                logger.info(f"running job: {type(job)}, dry_run={details.dry_run}")
                job.run(
                    source=details.source,
                    sink=details.sink,
                    start_time=current_time,
                    end_time=interval_end,
                    dry_run=details.dry_run
                )

            # Move to the next interval.
            current_time = interval_end


def main() -> int:
    parser = setup_parser()
    args = parser.parse_args()

    try:
        run_details = build_config(args)
    except ValueError as exc:
        parser.error(str(exc))

    run_jobs(run_details)
    return 0

if __name__ == "__main__":
    sys.exit(main())