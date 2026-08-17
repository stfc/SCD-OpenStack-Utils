from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from unittest.mock import MagicMock, patch

import pytest

from thecount.jobs import Job
from thecount.main import run_jobs
from thecount.source import Source
from thecount.sink import Sink
from thecount.structs import RunDetails

class StopLoop(Exception):
    """Sentinel to break out of the unbounded `while True`."""

class TestJob(Job):
    """Base for fake jobs; subclasses get their own `calls` list."""

    def __init__(self, limit: int | None = None, name: str = "jobA"):
        super().__init__()
        self.name = name
        self.limit = limit
        self.calls = []

    def run(
            self,
            source: Source,
            sink: Sink,
            start_time: datetime,
            end_time: datetime,
            dry_run=False
    ):
        self.calls.append(
            dict(start=start_time, end=end_time, dry_run=dry_run,
                 sink=sink, source=source)
        )
        # a way to stop an endless loop
        if self.limit is not None and len(self.calls) >= self.limit:
            raise StopLoop

    @staticmethod
    def _transform(rows: List[Dict[str, Any]], end_time: datetime, instance):
        raise NotImplementedError("this is a test class")


def make_job(name: str, limit: int | None = None) -> TestJob:
    """ helper to create a TestJob class and set the name/looping limit """
    test_job = TestJob()
    test_job.name = name
    test_job.limit = limit
    return test_job


def setup_run_details(
        jobs: List[Job],
        interval: timedelta,
        start_time: datetime,
        end_time: datetime | None,
        dry_run: bool = False
) -> RunDetails:
    """ helper to construct a RunDetails dataclass for tests """
    return RunDetails(
        source=MagicMock(),
        sink=MagicMock(),
        jobs=jobs,
        dry_run=dry_run,
        interval=interval,
        start_time=start_time,
        end_time=end_time,
    )

@pytest.fixture(autouse=True)
def stub_sleep():
    """ stubs out sleep for testing """
    with patch("thecount.__main__.time.sleep") as sleep:
        yield sleep


def test_run_jobs_one_interval():
    """ tests run loop runs once when one interval between start and end time """
    job = make_job("foo")
    interval = timedelta(hours=1)
    start_time = datetime(2026, 1, 1, 0, tzinfo=timezone.utc)
    end_time = datetime(2026, 1, 1, 1, tzinfo=timezone.utc)
    run_jobs(setup_run_details([job], interval, start_time, end_time))
    assert len(job.calls) == 1
    assert job.calls[0]["start"] == start_time
    assert job.calls[0]["end"] == end_time

def test_run_jobs_multiple_contiguous_intervals():
    """
    tests run loop runs more than once when start time and end time can be
    broken up into multiple intervals
    """
    job = make_job("foo")
    interval = timedelta(hours=1)
    start_time = datetime(2026, 1, 1, 0, tzinfo=timezone.utc)
    end_time = datetime(2026, 1, 1, 3, tzinfo=timezone.utc)

    run_jobs(setup_run_details([job], interval, start_time, end_time))

    bounds = [(c["start"], c["end"]) for c in job.calls]
    assert bounds == [
        (start_time, start_time + interval),
        (start_time + interval, start_time + 2 * interval),
        (start_time + 2 * interval, start_time + 3 * interval),
    ]

def test_run_jobs_partial_interval_ignored():
    """ tests that trailing time window too small for a full interval before end-time is ignored """
    job = make_job("foo")
    interval = timedelta(hours=1)
    start_time = datetime(2026, 1, 1, 0, tzinfo=timezone.utc)
    end_time = datetime(2026, 1, 1, 3, 30, tzinfo=timezone.utc)

    run_jobs(setup_run_details([job], interval, start_time, end_time))

    assert len(job.calls) == 3
    assert job.calls[-1]["end"] == start_time + 3 * interval


def test_run_jobs_ignores_large_interval():
    """ tests if the interval is too big between start and end time, should return nothing """

    job = make_job("foo")
    interval = timedelta(hours=1)
    start_time = datetime(2026, 1, 1, 0, tzinfo=timezone.utc)
    end_time = datetime(2026, 1, 1, 0, 30, tzinfo=timezone.utc)

    run_jobs(setup_run_details([job], interval, start_time, end_time))
    assert len(job.calls) == 0

def test_run_jobs_multiple_jobs_one_interval():
    """ tests that multiple jobs run per interval """
    a, b = make_job("a"), make_job("b")
    interval = timedelta(hours=1)
    start_time = datetime(2026, 1, 1, 0, tzinfo=timezone.utc)
    end_time = datetime(2026, 1, 1, 2, tzinfo=timezone.utc)

    run_jobs(setup_run_details([a, b], interval, start_time, end_time))
    assert len(a.calls) == 2 and len(b.calls) == 2
    assert [c["start"] for c in a.calls] == [c["start"] for c in b.calls]

def test_run_job_sleeps_when_interval_end_in_future(stub_sleep):
    """
    tests that run_jobs() sleeps when interval end is calculated as in the future
    and then calls jobs.run() after sleeping
     """
    job = make_job("foo")
    interval = timedelta(hours=1)
    start_time = datetime.now(timezone.utc)
    end_time = datetime.now(timezone.utc) + interval

    stub_sleep.side_effect = lambda s: job.calls.append("sleep")

    run_jobs(setup_run_details([job], interval, start_time, end_time))
    # should sleep once
    stub_sleep.assert_called_once()

    # should sleep approx 1 hour - might be slight differences based on when it executes
    assert stub_sleep.call_args.args[0] == pytest.approx(3600, abs=5)
    # should be two calls - [sleep, run()]
    assert len(job.calls) == 2
    # ensure sleep call was run before run() call
    assert job.calls[0] == "sleep"

def test_runs_indefinitely_without_end_time():
    """ tests that continuous looping works """

    job = make_job("foo", limit=5) # break continuous loop at 5 loops
    interval = timedelta(hours=1)
    start_time = datetime.now(timezone.utc)
    with pytest.raises(StopLoop):
        run_jobs(setup_run_details([job], interval, start_time, None))

    assert len(job.calls) == 5
    assert job.calls[-1]["end"] == start_time + 5 * interval