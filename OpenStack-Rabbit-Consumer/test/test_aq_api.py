from unittest.mock import patch, call

import pytest

from src.aq_api import verify_kerberos_ticket


def test_verify_kerberos_ticket_valid():
    with patch("src.aq_api.subprocess.call") as mocked_call:
        # Exit code 0 - i.e. valid ticket
        mocked_call.return_value = 0
        assert verify_kerberos_ticket()
        mocked_call.assert_called_once_with(["klist", "-s"])


@patch("src.aq_api.subprocess.call")
@patch("src.aq_api.common.config")
def test_verify_kerberos_ticket_renew(config, subprocess):
    # Exit code 1 - i.e. invalid ticket
    # Then 0 (kinit), 0 (klist -s)
    subprocess.side_effect = [1, 0, 0]

    assert verify_kerberos_ticket()

    config.get.assert_called_once_with("kerberos", "suffix", fallback="")
    assert subprocess.call_args_list == [
        call(["klist", "-s"]),
        call(["kinit", "-k", config.get.return_value]),
        call(["klist", "-s"]),
    ]


@patch("src.aq_api.subprocess.call")
@patch("src.aq_api.common.config")
def test_verify_kerberos_ticket_renew_empty_conf(config, subprocess):
    # Exit code 1 - i.e. invalid ticket
    # Then 0 (kinit), 0 (klist -s)
    subprocess.side_effect = [1, 0, 0]
    config.get.return_value = ""

    assert verify_kerberos_ticket()

    config.get.assert_called_once_with("kerberos", "suffix", fallback="")
    assert subprocess.call_args_list == [
        call(["klist", "-s"]),
        call(["kinit", "-k"]),
        call(["klist", "-s"]),
    ]


@patch("src.aq_api.subprocess.call")
@patch("src.aq_api.common.config")
def test_verify_kerberos_ticket_raises(config, subprocess):
    # Exit code 1 - i.e. invalid ticket
    # Then 0 (kinit), 1 (klist -s)
    subprocess.side_effect = [1, 0, 1]
    config.get.return_value = ""

    with pytest.raises(RuntimeError):
        verify_kerberos_ticket()

    config.get.assert_called_once_with("kerberos", "suffix", fallback="")
    assert subprocess.call_args_list == [
        call(["klist", "-s"]),
        call(["kinit", "-k"]),
        call(["klist", "-s"]),
    ]
