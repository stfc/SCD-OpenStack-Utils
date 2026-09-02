from datetime import datetime, timezone
from unittest.mock import patch
import configparser

import pytest

from thecount.source import Source, QUERY

START = datetime(2026, 1, 1, 9, 30, tzinfo=timezone.utc)
END = datetime(2026, 1, 2, 10, 45, tzinfo=timezone.utc)

MOCK_SOURCE_ENV_VARS = {
    "THE_COUNT_SOURCE_HOST": "localhost",
    "THE_COUNT_SOURCE_USERNAME": "admin",
    "THE_COUNT_SOURCE_PASSWORD": "pass",
}


@pytest.fixture(name="valid_config_file")
def valid_config_file_fn(tmp_path):
    """mocks a valid config file thecount.conf"""
    path = tmp_path / "t1.conf"
    path.write_text("[source]\nport = 3306\n")
    return path


def test_reads_connection_string(monkeypatch, valid_config_file):
    """test that connection string is read correctly from config file"""

    for env_var, value in MOCK_SOURCE_ENV_VARS.items():
        monkeypatch.setenv(env_var, value)

    assert (
        Source(str(valid_config_file)).conn_string
        == "mysql+pymysql://admin:pass@localhost:3306"
    )


def test_reads_fail_when_file_not_found():
    """tests that file not found error raised when provided a filepath that doesn't exist"""
    with pytest.raises(FileNotFoundError, match="config not found"):
        Source(str("na.conf"))


def test_missing_section_raises(tmp_path):
    """tests that error raised when provided a config file without relevant "source" section"""
    path = tmp_path / "t2.conf"
    path.write_text("[foo]\nbar = x\n")
    with pytest.raises(configparser.NoSectionError):
        Source(str(path))


def test_missing_key_raises(tmp_path):
    """tests that error is raised when provided a config file with "source" section but no "connection" var"""
    path = tmp_path / "t3.conf"
    path.write_text("[source]\nother = x\n")
    with pytest.raises(configparser.NoOptionError):
        Source(str(path))


@pytest.mark.parametrize("omitted_env_var", MOCK_SOURCE_ENV_VARS.keys())
def test_env_var_missing_raises(monkeypatch, omitted_env_var, valid_config_file):
    """tests that omitting an required environment variable raises error"""
    for env_var, val in MOCK_SOURCE_ENV_VARS.items():
        monkeypatch.setenv(env_var, val)

    # test that omitting env_var raises
    monkeypatch.setenv(omitted_env_var, "")

    with pytest.raises(ValueError, match=omitted_env_var):
        Source(str(valid_config_file))


def test_fetch_outside_with_block_raises(monkeypatch, valid_config_file):
    """tests that error is raised when instantiating Source outside a with block"""

    for env_var, value in MOCK_SOURCE_ENV_VARS.items():
        monkeypatch.setenv(env_var, value)

    with pytest.raises(RuntimeError):
        Source(str(valid_config_file)).fetch("nova", START, END)


@patch("thecount.source.Session")
@patch("thecount.source.sqlalchemy.create_engine")
def test_fetch_returns_rows_as_dicts(
    mock_create_engine, mock_session_cls, monkeypatch, valid_config_file
):
    """test fetch calls database create_engine correctly"""

    for env_var, value in MOCK_SOURCE_ENV_VARS.items():
        monkeypatch.setenv(env_var, value)

    mock_session = mock_session_cls.return_value.__enter__.return_value
    mock_session.execute.return_value.mappings.return_value = [
        {"foo": 1, "bar": "alpha"},
        {"foo": 2, "bar": "beta"},
    ]

    with Source(str(valid_config_file)) as source:
        result = source.fetch("nova", START, END)

    mock_create_engine.assert_called_once_with(
        "mysql+pymysql://admin:pass@localhost:3306/nova",
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=1,
        max_overflow=0,
    )

    # assert session called with proper args
    args, _ = mock_session.execute.call_args
    assert args[0] is QUERY  # TextClause has no useful __eq__, compare identity
    assert args[1] == {"start": "2026-01-01 09:30", "end": "2026-01-02 10:45"}

    # assert results are the parsed results of calling session.execute().mappings()
    assert result[0] == {"foo": 1, "bar": "alpha"}
    assert result[1] == {"foo": 2, "bar": "beta"}
