from unittest.mock import patch
import configparser

import pytest

from thecount.sink import Sink, TIMEOUT

DATASTRING = "cpu,host=a value=1 1700000000\ncpu,host=b value=2 1700000000"

@pytest.fixture()
def valid_config_file(tmp_path):
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

def test_reads_fail_when_file_not_found(tmp_path):
    """ tests that file not found error raised when provided a filepath that doesn't exist """
    with pytest.raises(FileNotFoundError, match="config not found"):
        Sink(str("na.conf"))


def test_missing_section_raises(tmp_path):
    """ tests that error raised when provided a config file without relevant "sink" section """
    path = tmp_path / "t1.conf"
    path.write_text("[foo]\nbar = x\n")
    with pytest.raises(configparser.NoSectionError):
        Sink(str(path))


def test_read_missing_key_raises(tmp_path):
    """ tests that error is raised when provided a config file with "sink" section but relevant keys missing """
    path = tmp_path / "t2.conf"
    path.write_text("[sink]\nbar = x\n")
    with pytest.raises(configparser.NoOptionError):
        Sink(str(path))


@patch('thecount.sink.requests.Session')
def test_write_success(mock_request_session, valid_config_file):
    """ test write sets up proper session and posts correct data """

    mock_session = mock_request_session.return_value
    mock_session.post.return_value.ok = True



    with Sink(str(valid_config_file)) as sink:
        sink.write(DATASTRING)

    mock_request_session.assert_called_once()
    mock_session.post.assert_called_once_with(
        "http://influx.example.com/write?db=accounting&precision=s",
        data=DATASTRING,
        timeout=TIMEOUT
    )
    assert sink.instance == "preprod"


@patch('thecount.sink.requests.Session')
def test_write_fail(mock_request_session, valid_config_file):
    """ raises runtime error if session.post().ok returns response that is not True """
    mock_session = mock_request_session.return_value
    mock_session.post.return_value.ok = False

    with pytest.raises(RuntimeError):
        with Sink(str(valid_config_file)) as sink:
            sink.write(DATASTRING)

    mock_request_session.assert_called_once()
    mock_session.post.assert_called_once_with(
        "http://influx.example.com/write?db=accounting&precision=s",
        data=DATASTRING,
        timeout=TIMEOUT
    )


@patch('thecount.sink.requests.Session')
def test_write_empty_datastring_does_nothing(mock_request_session, valid_config_file):
    """ tests that write doesn't post anything if provided an empty datastring """
    mock_session = mock_request_session.return_value

    with Sink(str(valid_config_file)) as sink:
        sink.write("")

    mock_request_session.assert_called_once()
    mock_session.post.assert_not_called()