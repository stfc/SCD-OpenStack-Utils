"""
Tests for utility functions for iriscasttools package
"""
import csv
import os
import pathlib
from unittest.mock import NonCallableMock, patch
import pytest
from utils import (
    to_csv,
    run_cmd,
    ipmi_raw_power_query,
    check_ipmi_conn,
    retry,
    get_ipmi_power_stats,
    get_ram_usage,
    get_os_load,
)

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_TESTDATA_DIR = os.path.join(_TEST_DIR, "test_data")


def read_test_from_file(test_fp, expected_out_fp):
    """
    Test "to_csv" function, turn Dictionary into comma spaced output

    Keyword arguments:
        test_fp -- str, filepath to example test file
        expected_out_fp -- str, filepath to example expected values as csv
    """
    with open(test_fp, "r", encoding="UTF-8") as txt_file:
        test_str = txt_file.read()

    with open(expected_out_fp, "r", encoding="UTF-8") as csv_file:
        csv_out = csv.DictReader(csv_file)
        for row in csv_out:
            expected_out = row
            break

    return test_str, expected_out


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
    Test "retry" decorator

    Keyword arguments:
        num_fail -- int: number of times command to retry is mocked to fail
        expected_calls -- int: number of times retry function is expected to call subprocess library
    """

    @retry(retry_on=(AssertionError,), retries=3, delay=1, backoff=1)
    def retry_func():
        retry_func.counter += 1
        if retry_func.counter > num_fail:
            return "success"
        raise AssertionError

    retry_func.counter = 0
    retry_func()
    assert retry_func.counter == expected_calls


@pytest.mark.parametrize(
    "valid_path",
    [
        ("/dev/ipmi0"),
        ("/dev/ipmi/0"),
        ("/dev/ipmidev/0"),
    ],
)
def test_check_ipmi_conn(valid_path):
    """
    Test "check_ipmi_conn" function

    Keyword arguments:
        valid_path: valid path to test
    """

    def mock_exists(file_path):
        return str(file_path) == valid_path

    with patch.object(pathlib.Path, "exists", mock_exists):
        assert check_ipmi_conn()


def test_check_ipmi_conn_fail():
    """
    Test "check_ipmi_conn" function return False when paths don't exist
    """
    with patch.object(pathlib.Path, "exists", lambda _: False):
        assert not check_ipmi_conn()


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


@pytest.mark.parametrize(
    "test_args",
    [
        (
            [
                "current_power",
                "minimum_power_over_sampling_duration",
                "maximum_power_over_sampling_duration",
                "average_power_over_sampling_duration",
                "time_stamp",
                "statistics_reporting_time_period",
                "power_management",
            ]
        ),
        (["some_invalid_arg"]),
    ],
)
@patch("utils.ipmi_raw_power_query")
@patch("utils.check_ipmi_conn")
def test_get_ipmi_power_stats(mock_check_ipmi_conn, mock_raw_power_query, test_args):
    """
    Test "ipmi_raw_power_query" function

    Keyword arguments:
        mock_raw_power_query -- mock

    """
    ipmi_example_fp = os.path.join(_TESTDATA_DIR, "raw_ipmi_test.txt")
    ipmi_example_exp_vals_fp = os.path.join(_TESTDATA_DIR, "raw_ipmi_test_exp_vals.csv")

    expected_results = {k: "" for k in test_args}
    raw_query_out, all_expected_vals_dict = read_test_from_file(
        ipmi_example_fp, ipmi_example_exp_vals_fp
    )

    mock_raw_power_query.return_value = raw_query_out
    mock_check_ipmi_conn.return_value = True
    expected_results.update(
        {
            k: v
            for k, v in all_expected_vals_dict.items()
            if k in expected_results.keys()
        }
    )

    result = get_ipmi_power_stats(*test_args)
    mock_check_ipmi_conn.assert_called_once()
    mock_raw_power_query.assert_called_once()
    assert result == expected_results


@pytest.mark.parametrize(
    "test_args",
    [(["max_ram_kb", "used_ram_kb", "ram_usage_percentage"]), (["some_invalid_arg"])],
)
@patch("utils.os.getloadavg")
def test_get_os_load(mock_os_get_load_avg, test_args):
    """
    Test "get_os_load" function

    Keyword arguments:
        mock_os_get_load_avg - mock os.getloadavg

    """
    # set ram usage out as arbitrary values
    expected_results = {k: "" for k in test_args}

    mock_values = {"os_load_1": 0.761, "os_load_5": 0.572, "os_load_15": 0.565}

    expected_results.update(
        {k: v for k, v in mock_values.items() if k in expected_results.keys()}
    )

    mock_os_get_load_avg.return_value = tuple(i for i in mock_values.values())

    result = get_os_load(*test_args)
    assert mock_os_get_load_avg.call_count == 1
    assert result == expected_results


@pytest.mark.parametrize(
    "test_args",
    [(["max_ram_kb", "used_ram_kb", "ram_usage_percentage"]), (["some_invalid_arg"])],
)
@patch("utils.run_cmd")
def test_get_ram_usage(mock_run_cmd, test_args):
    """
    Test "get_ram_usage" function

    Keyword arguments:
        mock_retry - mock object to mock retry and run command function

    """
    # set ram usage out as arbitrary values
    expected_results = {k: "" for k in test_args}

    mock_values = {"max_ram_kb": 1500000, "used_ram_kb": 1000000}
    mock_values["ram_usage_percentage"] = round(
        (mock_values["used_ram_kb"] / mock_values["max_ram_kb"]) * 100, 3
    )
    expected_results.update(
        {k: v for k, v in mock_values.items() if k in expected_results.keys()}
    )
    mock_run_cmd.side_effect = [
        str(mock_values["max_ram_kb"]),
        str(mock_values["used_ram_kb"]),
    ]

    result = get_ram_usage(*test_args)
    assert mock_run_cmd.call_count == 2
    assert result == expected_results
