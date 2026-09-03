import logging
from datetime import datetime
import time

from thecount.structs import RunDetails


logger = logging.getLogger(__name__)


def run_jobs(details: RunDetails) -> None:
    """
    function that runs jobs continuously at regular intervals until a specified end_time param reached.
    Sleeps between intervals.
    :param details: RunDetails object - containing parameters on what jobs to run and for how long
    """
    with details.source, details.sink:
        step_counter = 0
        current_time = details.start_time

        while True:
            step_counter += 1
            interval_end = current_time + details.interval

            # If there isn't a complete interval before end_time, stop.
            if details.end_time is not None and interval_end > details.end_time:
                logger.info("%s reached. Stopping...", details.end_time)
                break

            logger.info(
                "Starting Loop: %s: interval_start_time: %s, interval_end_time: %s",
                step_counter,
                current_time,
                interval_end,
            )

            # Don't start the process until end of the current interval - so all data is available
            now = datetime.now(current_time.tzinfo)
            if interval_end > now:
                logger.info("waiting until %s...", interval_end.isoformat())
                time.sleep((interval_end - now).total_seconds())

            # Run every job for this interval.
            for job in details.jobs:
                logger.info("running job: %s, dry_run=%s", type(job), details.dry_run)
                job.run(
                    source=details.source,
                    sink=details.sink,
                    start_time=current_time,
                    end_time=interval_end,
                    dry_run=details.dry_run,
                )

            # Move to the next interval.
            current_time = interval_end