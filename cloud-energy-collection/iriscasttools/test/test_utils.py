"""
Tests for utility functions for iriscasttools package
"""

from unittest.mock import NonCallableMock, Mock, patch
import pytest
from utils import to_csv, run_cmd, ipmi_raw_power_query, retry


@pytest.mark.parametrize(
    "mock_input, include_headers, expected_out",
    [
        (
            # test
            {"header1": "test", "header2": "1"},
            True,
            # expected
            "header1,header2\n" + "test,1",
        ),
        (  # test
            {"header1": "test", "header2": "1"},
            False,
            # expected
            "test,1",
        ),
    ],
)
def test_to_csv(mock_input, include_headers, expected_out):
    """
    Test "to_csv" function, turn Dictionary into comma spaced output

    Keyword arguments:
        mock_input -- Dict input for test
        include_headers -- bool, flag to set if output keys as header
        expected_out -- str, expected output for test
    """
    assert to_csv(mock_input, include_headers) == expected_out


@patch("utils.subprocess")
def test_run_cmd_success(mock_subprocess):
    """
    Test "run_cmd" function

    Keyword arguments:
        mock_subprocess -- Mock object for subprocess package
    """
    cmd_args = NonCallableMock()
    popen_mock_obj = mock_subprocess.Popen.return_value.__enter__

    stdout_mock = popen_mock_obj.return_value.stdout.read
    stderr_mock = popen_mock_obj.return_value.stderr.read

    stdout_mock.return_value = b"mock success"
    stderr_mock.return_value = b""

    cmd_stdout = run_cmd(cmd_args)
    mock_subprocess.Popen.assert_called_once_with(
        cmd_args, shell=True, stdout=mock_subprocess.PIPE, stderr=mock_subprocess.PIPE
    )
    assert cmd_stdout == "mock success"


@pytest.mark.parametrize("num_fail, expected_calls", [(0, 1), (1, 2), (2, 3)])
def test_retry(num_fail, expected_calls):
    """
    Test "retry" function

    Keyword arguments:
        num_fail -- int: number of times command to retry is mocked to fail
        expected_calls -- int: number of times retry function is expected to call subprocess library
    """
    mock = Mock()
    side_effects = [AssertionError for _ in range(num_fail)]
    side_effects.append("Success")

    mock.side_effect = side_effects

    retry(mock, retry_on=AssertionError, retries=3, delay=3, backoff=2)
    assert mock.call_count == expected_calls


@patch("utils.run_cmd")
def test_ipmi_raw_power_query(mock_run_cmd):
    """
    Test "ipmi_raw_power_query" function

    Keyword arguments:
        mock_run_cmd -- Mock object for utils.run_cmd function
    """
    val = ipmi_raw_power_query()
    mock_run_cmd.assert_called_once_with(
        "/usr/sbin/ipmi-dcmi --get-system-power-statistics"
    )
    assert val == mock_run_cmd.return_value
