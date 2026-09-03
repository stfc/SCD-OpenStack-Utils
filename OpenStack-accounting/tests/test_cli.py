import argparse
from unittest.mock import patch
from datetime import datetime, timezone, timedelta

import pytest
from conftest import ROOT_TEST_DATA_FP
from thecount.cli import setup_parser, build_config, ALL_JOBS


def make_args(**overrides) -> argparse.Namespace:
    """
    Helper function to create an argparse.Namespace - sets up using defaults and overrides based on inputs.
    used for testing build_config() function
    """

    # set config-path env variable
    defaults = {
        "job": None,
        "all": False,
        "start_time": None,
        "end_time": None,
        "interval": "3600",
        "dry_run": False,
        "config_path": ROOT_TEST_DATA_FP / "example.conf",
    }
    unknown = set(overrides) - set(defaults)
    if unknown:
        raise AttributeError(f"no such arg: {', '.join(sorted(unknown))}")
    return argparse.Namespace(**{**defaults, **overrides})


@pytest.fixture(name="no_conn_setup", autouse=True)
def no_connections():
    """Sink/Source are built inside build_config and would open sockets."""
    with patch("thecount.cli.Sink") as sink, patch("thecount.cli.Source") as source:
        yield sink, source


def test_setup_parser_defaults():
    """test that defaults are set when no args passed"""
    parser = setup_parser()
    ns = parser.parse_args([])
    assert ns.job is None
    assert ns.all is False
    assert ns.start_time is None
    assert ns.end_time is None
    assert ns.dry_run is False


def test_setup_parser_job_flag():
    """tests that --job works correctly"""
    parser = setup_parser()

    ns = parser.parse_args(["--job", "cinder", "--job", "manila"])
    assert ns.job == ["cinder", "manila"]
    # splitting and validation happens downstream - so preserve incorrect values
    ns = parser.parse_args(["--job", "foo,bar"])
    assert ns.job == ["foo,bar"]
    #  tests that you must provide a value after --job
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--job"])
    assert exc.value.code == 2


def test_setup_parser_all_flag():
    """test all flag is set to true when --all provided"""
    parser = setup_parser()
    assert parser.parse_args(["--all"]).all is True


def test_setup_parser_unknown_argument_exits():
    """tests that unknown arguments raise SystemExit"""
    parser = setup_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--unknown"])
    assert exc.value.code == 2


def test_defaults_all_when_neither_job_nor_all_given():
    """test that when --job nor --all are given, we default to --all"""
    cfg = build_config(make_args())
    job_cls = set(type(job) for job in cfg.jobs)
    assert job_cls == set(ALL_JOBS.values())


def test_all_selects_every_job():
    """tests that passing all=True arg creates an object for every available job class"""
    cfg = build_config(make_args(all=True))
    job_cls = set(type(job) for job in cfg.jobs)
    assert job_cls == set(ALL_JOBS.values())


def test_single_job():
    """tests that single job object is created for valid job identifier"""
    cfg = build_config(make_args(job=["cinder"]))
    assert isinstance(cfg.jobs[0], ALL_JOBS["cinder"])


def test_job_values_split():
    """tests that providing multiple jobs works properly"""
    cfg = build_config(make_args(job=["cinder", "nova"]))
    job_cls = set(type(job) for job in cfg.jobs)
    expected_cls = [ALL_JOBS["cinder"], ALL_JOBS["nova"]]
    assert job_cls == set(expected_cls)


def test_job_values_no_whitespace_tolerated():
    """test that --job comma-spaced values with no whitespace is parsed correctly"""
    cfg = build_config(make_args(job=["cinder,nova"]))
    job_cls = set(type(job) for job in cfg.jobs)
    expected_cls = [ALL_JOBS["cinder"], ALL_JOBS["nova"]]
    assert job_cls == set(expected_cls)


def test_job_values_whitespace_tolerated():
    """test that --job comma-spaced values with whitespace is parsed properly"""
    cfg = build_config(make_args(job=["cinder,nova", "glance"]))
    job_cls = set(type(job) for job in cfg.jobs)
    expected_cls = [ALL_JOBS["cinder"], ALL_JOBS["nova"], ALL_JOBS["glance"]]
    assert job_cls == set(expected_cls)


def test_job_values_empty_vals_ignored():
    """test that multiple commas are handled correctly"""
    cfg = build_config(make_args(job=["cinder,,nova"]))
    job_cls = set(type(job) for job in cfg.jobs)
    expected_cls = [ALL_JOBS["cinder"], ALL_JOBS["nova"]]
    assert job_cls == set(expected_cls)


def test_duplicates_run_once():
    """test that duplicate jobs are removed and only set to run once"""
    cfg = build_config(make_args(job=["cinder", "nova,cinder"]))
    job_cls = set(type(job) for job in cfg.jobs)
    expected_cls = [ALL_JOBS["cinder"], ALL_JOBS["nova"]]
    assert job_cls == set(expected_cls)


def test_unknown_job_named_in_error():
    """test that unknown job names raise an error"""
    with pytest.raises(ValueError, match="foo"):
        build_config(make_args(job=["cinder,foo"]))


def test_start_defaults_to_yesterday_date_midnight():
    """test that start time sets now() time properly"""
    curr = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = curr - timedelta(days=1)
    cfg = build_config(make_args(all=True))
    assert cfg.start_time < curr
    assert cfg.start_time == yesterday


def test_end_defaults_to_none():
    """tests that end time defaults to None"""
    assert build_config(make_args(all=True)).end_time is None


def test_yyyymmdd_times_parse_correctly():
    """tests that ISO 8601 formatting strings are accepted"""
    cfg = build_config(
        make_args(all=True, start_time="2026-01-01", end_time="2026-01-02")
    )
    assert cfg.start_time == datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert cfg.end_time == datetime(2026, 1, 2, tzinfo=timezone.utc)


def test_start_after_end_rejected():
    """tests to check end time is always after start time - fails if not"""
    with pytest.raises(ValueError, match="before"):
        build_config(
            make_args(all=True, start_time="2026-02-01", end_time="2026-01-01")
        )


def test_start_equal_to_end_rejected():
    """test to check end_time and start_time are different"""
    with pytest.raises(ValueError, match="before"):
        build_config(
            make_args(all=True, start_time="2026-01-01", end_time="2026-01-01")
        )


def test_dry_run_passed_through():
    """test to check dry_run is passed through to output config"""
    assert build_config(make_args(all=True, dry_run=True)).dry_run is True


def test_sink_and_source_get_config_path(no_conn_setup):
    """tests that sink and source are created with correct config path from inputs"""
    sink, source = no_conn_setup
    build_config(make_args(all=True, config_path="/etc/thecount.ini"))
    sink.assert_called_once_with("/etc/thecount.ini")
    source.assert_called_once_with("/etc/thecount.ini")
