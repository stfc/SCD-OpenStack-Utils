"""
Tests for main functions for iriscasttools package
"""

from unittest.mock import patch
import pytest

from main import get_iriscast_stats, parse_args


@pytest.mark.parametrize(
    "test_args, expected_arg_values",
    [
        (["--as-csv"], {"as_csv": True, "include_header": False}),
        (["-c"], {"as_csv": True, "include_header": False}),
        # include header ignored when csv is False
        (["--include-header"], {"as_csv": False, "include_header": False}),
        (["-i"], {"as_csv": False, "include_header": False}),
        (["--as-csv", "--include-header"], {"as_csv": True, "include_header": True}),
    ],
)
def test_parse_args(test_args, expected_arg_values):
    res = parse_args(test_args)
    assert vars(res) == expected_arg_values


@pytest.mark.parametrize(
    "test_csv_flag, test_include_header",
    [(False, False), (True, True), (True, False)],
)
@patch("utils.get_ipmi_power_stats")
@patch("utils.get_os_load")
@patch("utils.get_ram_usage")
@patch("utils.to_csv")
def test_get_iriscast_stats(
    mock_to_csv,
    mock_get_ram_usage,
    mock_get_os_load,
    mock_get_ipmi_power_stats,
    test_csv_flag,
    test_include_header,
):
    """
    Test get iriscast stats function

    Keyword arguments:
        - mock_get_ipmi_power_stats -- Mock obj for get_ipmi_power_stats
        - test_poll_period -- int, intervals between each reading, used to calculate watt hours
    """

    expected_power_stats = {"current_power": ""}
    expected_os_load_stats = {"os_load_5": ""}
    expected_ram_stats = {"ram_usage_percentage": ""}

    expected_all = dict(expected_power_stats)
    expected_all.update(expected_os_load_stats)
    expected_all.update(expected_ram_stats)

    mock_get_ipmi_power_stats.side_effect = [expected_power_stats]
    mock_get_os_load.return_value = expected_os_load_stats
    mock_get_ram_usage.return_value = expected_ram_stats

    _ = get_iriscast_stats(test_csv_flag, test_include_header)

    mock_get_ipmi_power_stats.assert_called_once_with("current_power")
    mock_get_os_load.assert_called_once_with("os_load_5")
    mock_get_ram_usage.assert_called_once_with("ram_usage_percentage")

    if test_csv_flag:
        mock_to_csv.assert_called_once_with(expected_all, test_include_header)
    else:
        assert not mock_to_csv.called
