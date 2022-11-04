from unittest import mock
from unittest.mock import patch, call, NonCallableMock

import pytest

from rabbit_consumer.aq_api import (
    verify_kerberos_ticket,
    setup_requests,
    aq_make,
    aq_manage,
    create_machine,
    delete_machine,
    create_host,
    delete_host,
    add_machine_interface,
    del_machine_interface_address,
    update_machine_interface,
    check_host_exists,
    set_env,
)


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


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.common.config")
def test_aq_manage(config, setup):
    env_type, env_name = "type", "name"
    host = "mocked_host"
    config.get.return_value = "https://example.com"

    aq_manage(host, env_type, env_name)

    config.get.assert_called_once_with("aquilon", "url")
    setup.assert_called_once()
    expected_url = "https://example.com/host/mocked_host/command/manage?hostname=mocked_host&type=name&force=true"
    assert setup.call_args == call(expected_url, "post", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.common.config")
def test_aq_create_machine(config, setup):
    uuid, prefix = "uuid_mock", "prefix_mock"
    vmhost, vcpus = "vmhost_mock", "vcpus_mock"
    memory, hostname = "memory_mock", "hostname_mock"

    config.get.return_value = "https://example.com"
    returned = create_machine(uuid, vmhost, vcpus, memory, hostname, prefix)

    config.get.assert_called_once_with("aquilon", "url")
    setup.assert_called_once()
    assert returned == setup.return_value
    expected_url = "https://example.com/next_machine/prefix_mock?model=vm-openstack&serial=uuid_mock&vmhost=vmhost_mock&cpucount=vcpus_mock&memory=memory_mock"
    assert setup.call_args == call(expected_url, "put", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.common.config")
def test_aq_delete_machine(config, setup):
    machine_name = "name_mock"

    config.get.return_value = "https://example.com"
    delete_machine(machine_name)

    config.get.assert_called_once_with("aquilon", "url")
    setup.assert_called_once()
    expected_url = "https://example.com/machine/name_mock"
    assert setup.call_args == call(expected_url, "delete", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.common.config")
def test_aq_create_machine(config, setup):
    host, machine = "host_str", "machine_str"
    sandbox, first_ip = "sandbox_str", "ip_str"
    archetype, domain = "arch_str", "domain_str"
    personality = "pers_str"
    os_name, os_version = "name_str", "vers_str"

    # Based on the order of calls in the impl
    config.get.side_effect = [
        "def_domain_str",
        "def_pers_str",
        "def_arch_str",
        "https://example.com",
    ]
    create_host(
        host,
        machine,
        sandbox,
        first_ip,
        archetype,
        domain,
        personality,
        os_name,
        os_version,
    )
    config.get.assert_has_calls(
        [
            call("aquilon", "url"),
            call("aquilon", "default_domain"),
            call("aquilon", "default_personality"),
            call("aquilon", "default_archetype"),
        ],
        any_order=True,
    )

    setup.assert_called_once()
    expected_url = "https://example.com/host/host_str?machine=machine_str&ip=ip_str&archetype=def_arch_str&domain=def_domain_str&personality=def_pers_str&osname=name_str&osversion=vers_str"
    assert setup.call_args == call(expected_url, "put", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.common.config")
def test_aq_delete_host(config, setup):
    machine_name = "name_mock"

    config.get.return_value = "https://example.com"
    delete_host(machine_name)

    config.get.assert_called_once_with("aquilon", "url")
    setup.assert_called_once()
    expected_url = "https://example.com/host/name_mock"
    assert setup.call_args == call(expected_url, "delete", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.common.config")
def test_add_machine_interface(config, setup):
    # Other attrs are unused
    machine_name = "name_str"
    mac_addr = "mac_addr"
    interface_name = "iface_name"

    config.get.return_value = "https://example.com"
    add_machine_interface(
        machine_name,
        ipaddr="",
        macaddr=mac_addr,
        label="",
        interfacename=interface_name,
        hostname="",
    )

    setup.assert_called_once()
    expected_url = (
        "https://example.com/machine/name_str/interface/iface_name?mac=mac_addr"
    )
    assert setup.call_args == call(expected_url, "put", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.common.config")
def test_delete_machine_interface(config, setup):
    host_name = "name_str"
    machine_name = "machine_str"
    interface_name = "iface_name"

    config.get.return_value = "https://example.com"
    del_machine_interface_address(
        host_name, machinename=machine_name, interfacename=interface_name
    )

    setup.assert_called_once()
    expected_url = "https://example.com/interface_address?machine=machine_str&interface=iface_name&fqdn=name_str"
    assert setup.call_args == call(expected_url, "delete", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.common.config")
def test_update_machine_interface(config, setup):
    machine_name = "machine_str"
    interface_name = "iface_name"

    config.get.return_value = "https://example.com"
    update_machine_interface(machinename=machine_name, interfacename=interface_name)

    setup.assert_called_once()
    expected_url = "https://example.com/machine/machine_str/interface/iface_name?boot&default_route"
    assert setup.call_args == call(expected_url, "post", mock.ANY)


@patch("rabbit_consumer.aq_api.setup_requests")
@patch("rabbit_consumer.aq_api.common.config")
def test_check_host_exists(config, setup):
    hostname = "host_str"

    config.get.return_value = "https://example.com"
    check_host_exists(hostname)

    expected_url = f"{config.get.return_value}/host/{hostname}"
    setup.assert_called_once_with(expected_url, "get", mock.ANY)


@pytest.mark.parametrize("domain", ["set", ""])
@patch("rabbit_consumer.aq_api.aq_manage")
@patch("rabbit_consumer.aq_api.aq_make")
def test_set_env_selects_domain_or_sandbox(_, manage, domain):
    hostname = NonCallableMock()
    sandbox = NonCallableMock()

    # TODO we should check if sandbox is actually set
    set_env(hostname, domain=domain, sandbox=sandbox)

    selected_method = "domain" if domain else "sandbox"
    selected_obj = domain if domain else sandbox
    manage.assert_called_once_with(hostname, selected_method, selected_obj)


@patch("rabbit_consumer.aq_api.aq_manage")
@patch("rabbit_consumer.aq_api.aq_make")
def test_set_env_calls_make(make, _):
    host, domain = NonCallableMock(), NonCallableMock()
    sandbox, personality = NonCallableMock(), NonCallableMock()
    os_version, os_name = NonCallableMock(), NonCallableMock()
    arch = NonCallableMock()

    set_env(host, domain, sandbox, personality, os_version, arch, os_name)

    make.assert_called_once_with(host, personality, os_version, arch, os_name)
