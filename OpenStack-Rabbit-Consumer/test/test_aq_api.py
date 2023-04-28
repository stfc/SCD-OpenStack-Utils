from dataclasses import dataclass
from unittest import mock
from unittest.mock import patch, call, NonCallableMock

import pytest

# noinspection PyUnresolvedReferences
# pylint: disable=unused-import
from fixtures import (
    fixture_rabbit_message,
    fixture_vm_data,
    fixture_openstack_address_list,
    fixture_openstack_address,
)
from rabbit_consumer.aq_api import (
    verify_kerberos_ticket,
    setup_requests,
    aq_make,
    aq_manage,
    create_machine,
    delete_machine,
    create_host,
    delete_host,
    set_interface_bootable,
    check_host_exists,
    AquilonError,
    add_machine_nics,
)
from rabbit_consumer.os_descriptions.os_descriptions import OsDescription


def test_verify_kerberos_ticket_valid():
    with patch("rabbit_consumer.aq_api.subprocess.call") as mocked_call:
        # Exit code 0 - i.e. valid ticket
        mocked_call.return_value = 0
        assert verify_kerberos_ticket()
        mocked_call.assert_called_once_with(["klist", "-s"])


@patch("rabbit_consumer.aq_api.subprocess.call")
def test_verify_kerberos_ticket_invalid(subprocess):
    # Exit code 1 - i.e. invalid ticket
    # Then 0 (kinit), 0 (klist -s)
    subprocess.side_effect = [1]

    with pytest.raises(RuntimeError):
        verify_kerberos_ticket()

    subprocess.assert_called_once_with(["klist", "-s"])


@patch("rabbit_consumer.aq_api.requests")
@patch("rabbit_consumer.aq_api.Retry")
@patch("rabbit_consumer.aq_api.HTTPAdapter")
@patch("rabbit_consumer.aq_api.verify_kerberos_ticket")
def test_setup_requests(verify_kerb, adapter, retry, requests):
    session = requests.Session.return_value
    response = session.get.return_value
    response.status_code = 200

    setup_requests(NonCallableMock(), NonCallableMock(), NonCallableMock())
    assert (
        session.verify
        == "/etc/grid-security/certificates/aquilon-gridpp-rl-ac-uk-chain.pem"
    )

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

    with pytest.raises(ConnectionError):
        setup_requests(NonCallableMock(), NonCallableMock(), NonCallableMock())

    assert (
        session.verify
        == "/etc/grid-security/certificates/aquilon-gridpp-rl-ac-uk-chain.pem"
    )

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
    url, desc, params = NonCallableMock(), NonCallableMock(), NonCallableMock()

    session = requests.Session.return_value

    rest_method = getattr(session, rest_verb)
    response = rest_method.return_value
    response.status_code = 200

    assert setup_requests(url, rest_verb, desc, params) == response.text
    rest_method.assert_called_once_with(url, auth=kerb_auth.return_value, params=params)


@dataclass
class MockOs(OsDescription):
    """
    Represents a mock OS description for testing purposes
    """

    aq_os_name = NonCallableMock()
    aq_os_version = NonCallableMock()
    aq_default_personality = NonCallableMock()
    os_identifiers = []


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.ConsumerConfig")
def test_aq_make_calls(config, setup, openstack_address_list):
    domain = "domain"
    config.return_value.aq_url = domain

    mocked_os_details = MockOs()

    aq_make(openstack_address_list, mocked_os_details)

    expected_params = {
        "personality": mocked_os_details.aq_default_personality,
        "osversion": mocked_os_details.aq_os_version,
        "osname": mocked_os_details.aq_os_name,
        "archetype": "cloud",
    }

    expected_urls = [
        f"{domain}/host/{net.hostname}/command/make" for net in openstack_address_list
    ]
    setup.assert_has_calls(
        [
            call(expected_urls[0], "post", mock.ANY, expected_params),
            call(expected_urls[1], "post", mock.ANY, expected_params),
        ]
    )


@pytest.mark.parametrize(
    "field_to_blank",
    [
        "aq_default_personality",
        "aq_os_name",
        "aq_os_version",
    ],
)
@patch("rabbit_consumer.aq_api.ConsumerConfig")
def test_aq_make_missing_fields(config, field_to_blank, openstack_address_list):
    domain = "https://example.com"

    os = MockOs()

    config.return_value.aq_url = domain

    with pytest.raises(AssertionError):
        setattr(os, field_to_blank, None)
        aq_make(openstack_address_list, os)

    with pytest.raises(AssertionError):
        setattr(os, field_to_blank, "")
        aq_make(openstack_address_list, os)


@pytest.mark.parametrize("hostname", ["  ", "", None])
@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.ConsumerConfig")
def test_aq_make_none_hostname(config, setup, openstack_address, hostname):
    domain = "https://example.com"
    config.return_value.aq_url = domain

    address = openstack_address
    address.hostname = hostname

    with pytest.raises(ValueError):
        aq_make([address], NonCallableMock())

    setup.assert_not_called()


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.ConsumerConfig")
def test_aq_manage(config, setup, openstack_address_list):
    config.return_value.aq_url = "https://example.com"

    aq_manage(openstack_address_list)

    params = [
        {
            "hostname": net.hostname,
            "domain": config.return_value.aq_domain,
            "force": True,
        }
        for net in openstack_address_list
    ]

    expected_urls = [
        f"https://example.com/host/{i.hostname}/command/manage"
        for i in openstack_address_list
    ]
    setup.assert_has_calls(
        [
            call(expected_urls[0], "post", mock.ANY, params=params[0]),
            call(expected_urls[1], "post", mock.ANY, params=params[1]),
        ]
    )


@patch("rabbit_consumer.aq_api.ConsumerConfig")
@patch("rabbit_consumer.aq_api.setup_requests")
def test_aq_create_machine(setup, config, rabbit_message, vm_data):
    config.return_value.aq_url = "https://example.com"
    config.return_value.aq_prefix = "prefix_mock"

    returned = create_machine(rabbit_message, vm_data)

    expected_args = {
        "model": "vm-openstack",
        "serial": vm_data.virtual_machine_id,
        "vmhost": rabbit_message.payload.vm_host,
        "cpucount": rabbit_message.payload.vcpus,
        "memory": rabbit_message.payload.memory_mb,
    }

    expected_url = "https://example.com/next_machine/prefix_mock"
    assert setup.call_args == call(expected_url, "put", mock.ANY, params=expected_args)
    assert returned == setup.return_value


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.ConsumerConfig")
def test_aq_delete_machine(config, setup):
    machine_name = "name_mock"

    config.return_value.aq_url = "https://example.com"
    delete_machine(machine_name)

    setup.assert_called_once()
    expected_url = "https://example.com/machine/name_mock"
    assert setup.call_args == call(expected_url, "delete", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.ConsumerConfig")
def test_aq_create_host(config, setup, openstack_address_list):
    machine_name = "machine_name_str"
    os_desc = NonCallableMock()

    env_config = config.return_value
    env_config.aq_url = "https://example.com"

    create_host(os_desc, openstack_address_list, machine_name)

    expected_params = [
        {
            "machine": machine_name,
            "ip": net.addr,
            "archetype": env_config.aq_archetype,
            "domain": env_config.aq_domain,
            "personality": env_config.aq_personality,
            "osname": os_desc.aq_os_name,
            "osversion": os_desc.aq_os_version,
        }
        for net in openstack_address_list
    ]

    expected_urls = [
        f"https://example.com/host/{i.hostname}" for i in openstack_address_list
    ]
    setup.assert_has_calls(
        [
            call(expected_urls[0], "put", mock.ANY, params=expected_params[0]),
            call(expected_urls[1], "put", mock.ANY, params=expected_params[1]),
        ]
    )


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.ConsumerConfig")
def test_aq_delete_host(config, setup):
    machine_name = "name_mock"

    config.return_value.aq_url = "https://example.com"
    delete_host(machine_name)

    setup.assert_called_once()
    expected_url = "https://example.com/host/name_mock"
    assert setup.call_args == call(expected_url, "delete", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.ConsumerConfig")
def test_add_machine_interface(config, setup, openstack_address_list):
    config.return_value.aq_url = "https://example.com"

    machine_name = "name_str"
    add_machine_nics(machine_name, openstack_address_list)

    iface_creation_urls = [
        f"https://example.com/machine/{machine_name}/interface/eth{i}"
        for i in range(len(openstack_address_list))
    ]

    update_params = [
        {
            "machine": machine_name,
            "interface": f"eth{i}",
            "ip": net.addr,
            "fqdn": net.hostname,
        }
        for i, net in enumerate(openstack_address_list)
    ]

    setup.assert_has_calls(
        [
            call(
                iface_creation_urls[0],
                "put",
                mock.ANY,
                params={"mac": openstack_address_list[0].mac_addr},
            ),
            call(
                "https://example.com/interface_address",
                "put",
                mock.ANY,
                params=update_params[0],
            ),
            call(
                iface_creation_urls[1],
                "put",
                mock.ANY,
                params={"mac": openstack_address_list[1].mac_addr},
            ),
            call(
                "https://example.com/interface_address",
                "put",
                mock.ANY,
                params=update_params[1],
            ),
        ]
    )


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.ConsumerConfig")
def test_update_machine_interface(config, setup):
    machine_name = "machine_str"
    interface_name = "iface_name"

    config.return_value.aq_url = "https://example.com"
    set_interface_bootable(machinename=machine_name, interfacename=interface_name)

    setup.assert_called_once()
    expected_url = "https://example.com/machine/machine_str/interface/iface_name?boot&default_route"
    assert setup.call_args == call(expected_url, "post", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.ConsumerConfig")
def test_check_host_exists(config, setup):
    hostname = "host_str"

    config.return_value.aq_url = "https://example.com"
    assert check_host_exists(hostname)

    expected_url = f"https://example.com/host/{hostname}"
    setup.assert_called_once_with(expected_url, "get", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.ConsumerConfig")
def test_check_host_exists_returns_false(config, setup):
    hostname = "host_str"
    config.return_value.aq_url = "https://example.com"
    setup.side_effect = AquilonError(f"Error:\n Host {hostname} not found.")

    assert not check_host_exists(hostname)
