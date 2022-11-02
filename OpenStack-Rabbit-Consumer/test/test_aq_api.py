from unittest import mock
from unittest.mock import patch, call, NonCallableMock

import pytest

from rabbit_consumer.aq_api import verify_kerberos_ticket, setup_requests, aq_make


def test_verify_kerberos_ticket_valid():
    with patch("rabbit_consumer.aq_api.subprocess.call") as mocked_call:
        # Exit code 0 - i.e. valid ticket
        mocked_call.return_value = 0
        assert verify_kerberos_ticket()
        mocked_call.assert_called_once_with(["klist", "-s"])


@patch("rabbit_consumer.aq_api.subprocess.call")
@patch("rabbit_consumer.aq_api.common.config")
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


@patch("rabbit_consumer.aq_api.subprocess.call")
@patch("rabbit_consumer.aq_api.common.config")
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


@patch("rabbit_consumer.aq_api.subprocess.call")
@patch("rabbit_consumer.aq_api.common.config")
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


@patch("rabbit_consumer.aq_api.requests")
@patch("rabbit_consumer.aq_api.Retry")
@patch("rabbit_consumer.aq_api.HTTPAdapter")
@patch("rabbit_consumer.aq_api.verify_kerberos_ticket")
def test_setup_requests(verify_kerb, adapter, retry, requests):
    session = requests.Session.return_value
    response = session.get.return_value
    response.status_code = 200

    setup_requests(NonCallableMock(), NonCallableMock(), NonCallableMock())
    assert session.verify == "/etc/grid-security/certificates/"

    verify_kerb.assert_called_once()
    retry.assert_called_once_with(total=5, backoff_factor=0.1, status_forcelist=[503])
    adapter.assert_called_once_with(max_retries=retry.return_value)
    session.mount.assert_called_once_with("https://", adapter.return_value)


@patch("rabbit_consumer.aq_api.requests")
@patch("rabbit_consumer.aq_api.Retry")
@patch("rabbit_consumer.aq_api.HTTPAdapter")
@patch("rabbit_consumer.aq_api.verify_kerberos_ticket")
def test_setup_requests_throws_for_failed(verify_kerb, adapter, retry, requests):
    session = requests.Session.return_value
    response = session.get.return_value
    response.status_code = 500

    with pytest.raises(Exception):
        setup_requests(NonCallableMock(), NonCallableMock(), NonCallableMock())

    assert session.verify == "/etc/grid-security/certificates/"

    verify_kerb.assert_called_once()
    retry.assert_called_once_with(total=5, backoff_factor=0.1, status_forcelist=[503])
    adapter.assert_called_once_with(max_retries=retry.return_value)
    session.mount.assert_called_once_with("https://", adapter.return_value)
    session.get.assert_called_once()


@pytest.mark.parametrize("rest_verb", ["get", "post", "put", "delete"])
@patch("rabbit_consumer.aq_api.requests")
@patch("rabbit_consumer.aq_api.HTTPKerberosAuth")
@patch("rabbit_consumer.aq_api.verify_kerberos_ticket")
def test_setup_requests_rest_methods(_, kerb_auth, requests, rest_verb):
    url, desc = NonCallableMock(), NonCallableMock()

    session = requests.Session.return_value

    rest_method = getattr(session, rest_verb)
    response = rest_method.return_value
    response.status_code = 200

    assert setup_requests(url, rest_verb, desc) == response.text
    rest_method.assert_called_once_with(url, auth=kerb_auth.return_value)


@patch("rabbit_consumer.aq_api.requests")
@patch("rabbit_consumer.aq_api.HTTPKerberosAuth")
@patch("rabbit_consumer.aq_api.verify_kerberos_ticket")
def test_setup_requests_get(_, kerb_auth, requests):
    url, desc = NonCallableMock(), NonCallableMock()
    session = requests.Session.return_value
    response = session.get.return_value
    response.status_code = 200

    assert setup_requests(url, "get", desc) == response.text

    session.get.assert_called_once_with(url, auth=kerb_auth.return_value)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.common.config")
def test_aq_make(config, setup):
    hostname = "host"
    personality = "pers"
    os_version = "osvers"
    archetype = "arch"
    os_name = "name"
    domain = "https://example.com"

    config.get.return_value = domain

    aq_make(hostname, personality, os_version, archetype, os_name)
    setup.assert_called_once()

    expected_url = f"{domain}/host/{hostname}/command/make?personality={personality}&osversion={os_version}&archetype={archetype}&osname={os_name}"
    assert setup.call_args == call(expected_url, "post", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.common.config")
def test_aq_make_whitespace(config, setup):
    hostname = "host"
    personality = " "
    os_version = "  "
    archetype = ""
    os_name = "name"
    domain = "https://example.com"

    config.get.return_value = domain

    aq_make(hostname, personality, os_version, archetype, os_name)
    setup.assert_called_once()

    expected_url = f"{domain}/host/{hostname}/command/make?osname={os_name}"
    assert setup.call_args == call(expected_url, "post", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.common.config")
def test_aq_make_none(config, setup):
    hostname = "my_host_name"
    personality = " "
    os_version = None
    archetype = ""
    os_name = None
    domain = "https://example.com"

    config.get.return_value = domain

    aq_make(hostname, personality, os_version, archetype, os_name)
    setup.assert_called_once()

    expected_url = f"{domain}/host/{hostname}/command/make"
    assert "?" not in expected_url  # Since there's no query params
    assert setup.call_args == call(expected_url, "post", mock.ANY)


@pytest.mark.parametrize("hostname", ["  ", "", None])
@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.common.config")
def test_aq_make_none_hostname(config, setup, hostname):
    domain = "https://example.com"

    config.get.return_value = domain

    with pytest.raises(ValueError):
        aq_make(hostname)

    setup.assert_not_called()
