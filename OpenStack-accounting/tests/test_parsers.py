import pytest

from conftest import (
    ROOT_TEST_DATA_FP,
    END_TIME,
    START_TIME,
    load_example_data,
    load_expected_data,
)
from thecount.parsers.glance_parser import GlanceParser
from thecount.parsers.cinder_parser import CinderParser
from thecount.parsers.manila_parser import ManilaParser
from thecount.parsers.nova_parser import NovaParser

JOBS = {
    "cinder": CinderParser,
    "nova": NovaParser,
    "manila": ManilaParser,
    "glance": GlanceParser,
}


@pytest.mark.parametrize("dirname", JOBS)
def test_job_output(dirname, mock_source, mock_sink):
    """
    for each set of example data in test_date, tests that job.run() is correctly runs
    example data contains:
        - input.txt -> loaded into dictionary that mocks output from source.fetch()
        - exp.txt -> contains comma-spaced string which is written to influxdb using sink.write()

    mocks source.fetch() returning contexts of input.txt, compares parsed output from _transform to exp.txt
    and ensures sink.write() is run correctly.

    """
    job_cls = JOBS[dirname]
    fixture_dir = ROOT_TEST_DATA_FP / dirname
    rows = load_example_data(fixture_dir / "input.txt")
    expected = load_expected_data(fixture_dir / "exp.txt")

    mock_source.fetch.return_value = rows
    job = job_cls()
    job.run(
        sink=mock_sink, source=mock_source, start_time=START_TIME, end_time=END_TIME
    )

    mock_source.fetch.assert_called_once_with(
        database=job_cls.db_name,
        start_time=START_TIME,
        end_time=END_TIME,
    )
    mock_sink.write.assert_called_once()
    actual = mock_sink.write.call_args.args[0]

    assert isinstance(actual, str), f"sink.write got {type(actual).__name__}"
    assert actual.splitlines() == expected.splitlines()


@pytest.mark.parametrize("dirname", JOBS)
def test_dry_run_does_not_write(dirname, mock_source, mock_sink):
    """test that when dry run is true, sink.write is not called"""
    mock_source.fetch.return_value = load_example_data(
        ROOT_TEST_DATA_FP / dirname / "input.txt"
    )
    JOBS[dirname]().run(
        sink=mock_sink,
        source=mock_source,
        start_time=START_TIME,
        end_time=END_TIME,
        dry_run=True,
    )
    mock_sink.write.assert_not_called()
