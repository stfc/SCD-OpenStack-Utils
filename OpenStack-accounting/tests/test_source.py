from datetime import datetime, timezone
from unittest.mock import patch
import configparser

import pytest

from thecount.source import Source, QUERY

START = datetime(2026, 1, 1, 9, 30, tzinfo=timezone.utc)
END = datetime(2026, 1, 2, 10, 45, tzinfo=timezone.utc)

@pytest.fixture
def valid_config_file(tmp_path):
    path = tmp_path / "t1.conf"
    path.write_text("[source]\nconnection = mysql+pymysql://dbuser:pass@exampledb:3306\n")
    return path

def test_reads_connection_string(valid_config_file):
    assert Source(str(valid_config_file)).conn_string == "mysql+pymysql://dbuser:pass@exampledb:3306"


def test_reads_fail_when_file_not_found(tmp_path):
    """ tests that file not found error raised when provided a filepath that doesn't exist """
    with pytest.raises(FileNotFoundError, match="config not found"):
        Source(str("na.conf"))


def test_missing_section_raises(tmp_path):
    """ tests that error raised when provided a config file without relevant "source" section """
    path = tmp_path / "t2.conf"
    path.write_text("[foo]\nbar = x\n")
    with pytest.raises(configparser.NoSectionError):
        Source(str(path))


def test_missing_key_raises(tmp_path):
    """ tests that error is raised when provided a config file with "source" section but no "connection" var """
    path = tmp_path / "t3.conf"
    path.write_text("[source]\nother = x\n")
    with pytest.raises(configparser.NoOptionError):
        Source(str(path))


def test_fetch_outside_with_block_raises(valid_config_file):
    with pytest.raises(RuntimeError):
        Source(str(valid_config_file)).fetch("nova", START, END)


@patch('thecount.source.Session')
@patch('thecount.source.sqlalchemy.create_engine')
def test_fetch_returns_rows_as_dicts(mock_create_engine, mock_session_cls, valid_config_file):
    """ test fetch calls database create_engine correctly """

    mock_session = mock_session_cls.return_value.__enter__.return_value
    mock_session.execute.return_value.mappings.return_value = [
        {"foo": 1, "bar": "alpha"},
        {"foo": 2, "bar": "beta"}
    ]

    with Source(str(valid_config_file)) as source:
        result = source.fetch("nova", START, END)

    mock_create_engine.assert_called_once_with(
        "mysql+pymysql://dbuser:pass@exampledb:3306/nova",
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

