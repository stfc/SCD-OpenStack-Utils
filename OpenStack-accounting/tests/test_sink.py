from unittest.mock import patch
import configparser

import pytest
from influxdb.exceptions import InfluxDBClientError

from thecount.sink import Sink, TIMEOUT

DATASTRING = "cpu,host=a value=1 1700000000\ncpu,host=b value=2 1700000000"
PARSED_DATASTRING = ["cpu,host=a value=1 1700000000", "cpu,host=b value=2 1700000000"]


@pytest.fixture(name="valid_config_file")
def valid_config_file_fn(tmp_path):
    """ creates a mock valid thecount.conf config file """
    path = tmp_path / "t3.conf"
    path.write_text(
        "[sink]\n"
        "host = influx.example.com\n"
        "database = accounting\n"
        "instance = preprod\n"
        "username = user\n"
        "password = pass\n",
        encoding="utf-8",
    )
    return path


def test_reads_fail_when_file_not_found():
    """tests that file not found error raised when provided a filepath that doesn't exist"""
    with pytest.raises(FileNotFoundError, match="config not found"):
        Sink(str("na.conf"))


def test_missing_section_raises(tmp_path):
    """tests that error raised when provided a config file without relevant "sink" section"""
    path = tmp_path / "t1.conf"
    path.write_text("[foo]\nbar = x\n")
    with pytest.raises(configparser.NoSectionError):
        Sink(str(path))


def test_read_missing_key_raises(tmp_path):
    """tests that error is raised when provided a config file with "sink" section but relevant keys missing"""
    path = tmp_path / "t2.conf"
    path.write_text("[sink]\nbar = x\n")
    with pytest.raises(configparser.NoOptionError):
        Sink(str(path))


@patch("thecount.sink.InfluxDBClient")
def test_write_success(mock_influxdb_client, valid_config_file):
    """test write sets up proper influxdb client and writes correct data"""

    mock_client = mock_influxdb_client.return_value

    with Sink(str(valid_config_file)) as sink:
        sink.write(DATASTRING)

    mock_client.write_points.assert_called_once_with(
        PARSED_DATASTRING, time_precision="s", protocol="line"
    )

    mock_influxdb_client.assert_called_once_with(
        host="influx.example.com",
        port=8086,
        username="user",
        password="pass",
        database="accounting",
        ssl=True,
        verify_ssl=False,
        timeout=TIMEOUT,
    )


@patch("thecount.sink.InfluxDBClient")
def test_write_fail(mock_influxdb_client, valid_config_file):
    """raises runtime error if influxdbclient write_points raises influxdbclient error"""
    mock_session = mock_influxdb_client.return_value
    mock_session.write_points.side_effect = InfluxDBClientError("foo")

    with pytest.raises(RuntimeError):
        with Sink(str(valid_config_file)) as sink:
            sink.write(DATASTRING)

    mock_influxdb_client.assert_called_once()
    mock_session.write_points.assert_called_once_with(
        PARSED_DATASTRING,
        time_precision="s",
        protocol="line",
    )


@patch("thecount.sink.InfluxDBClient")
def test_write_empty_datastring_does_nothing(mock_influxdb_client, valid_config_file):
    """tests that write doesn't post anything if provided an empty datastring"""
    mock_session = mock_influxdb_client.return_value

    with Sink(str(valid_config_file)) as sink:
        sink.write("")

    mock_influxdb_client.assert_called_once()
    mock_session.post.assert_not_called()
