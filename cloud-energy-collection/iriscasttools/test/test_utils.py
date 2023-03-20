import pytest
from utils import to_csv, run_cmd, ipmi_raw_power_query, retry
from unittest.mock import NonCallableMock, Mock, patch


@pytest.mark.parametrize(
    "mock, include_headers, expected_out",
    [(
        # test
        {"header1":"test", "header2":"1"}, True, 
            # expected
            "header1,header2\n"\
            "test,1"
    ),
    (    # test
        {"header1":"test", "header2":"1"}, False,
            #expected
            "test,1"
    )]
)
def test_to_csv(mock, include_headers, expected_out): 
    assert to_csv(mock, include_headers) == expected_out


@patch("utils.subprocess")
def test_run_cmd_success(mock_subprocess):
    cmd_args = NonCallableMock()
    popen_return = mock_subprocess.Popen.return_value
    popen_return.communicate.return_value = (None, None)
    run_cmd(cmd_args)
    mock_subprocess.Popen.assert_called_once_with(cmd_args, shell=True, stdout=mock_subprocess.PIPE, stderr=mock_subprocess.PIPE)


@pytest.mark.parametrize(
    "num_fail, expected_calls",
    [(0, 1), (1, 2), (2, 3)]
)
def test_retry(num_fail, expected_calls):
    mock = Mock()
    side_effects = [AssertionError for x in range(num_fail)]
    side_effects.append("Success")

    mock.side_effect = side_effects

    retry(mock, retry_on=AssertionError, retries=3, delay=3, backoff=2)
    assert mock.call_count == expected_calls

@patch("utils.run_cmd")
def test_ipmi_raw_power_query(mock_run_cmd):
    val = ipmi_raw_power_query()
    mock_run_cmd.assert_called_once_with("/usr/sbin/ipmi-dcmi --get-system-power-statistics")
    assert val == mock_run_cmd.return_value