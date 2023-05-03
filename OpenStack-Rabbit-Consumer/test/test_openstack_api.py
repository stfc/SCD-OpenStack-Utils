from unittest.mock import NonCallableMock, patch

# noinspection PyUnresolvedReferences
# pylint: disable=unused-import
from fixtures import fixture_vm_data
from rabbit_consumer.openstack_api import (
    update_metadata,
    OpenstackConnection,
    check_machine_exists,
    get_server_details,
    get_server_networks,
)


@patch("rabbit_consumer.openstack_api.ConsumerConfig")
@patch("rabbit_consumer.openstack_api.openstack.connect")
def test_openstack_connection(mock_connect, mock_config):
    """
    Test that the OpenstackConnection context manager calls the correct functions
    """
    mock_project = NonCallableMock()
    with OpenstackConnection(mock_project) as conn:
        mock_connect.assert_called_once_with(
            auth_url=mock_config.return_value.openstack_auth_url,
            project_name=mock_project,
            username=mock_config.return_value.openstack_username,
            password=mock_config.return_value.openstack_password,
            user_domain_name=mock_config.return_value.openstack_domain_name,
            project_domain_name="default",
        )

        assert conn == mock_connect.return_value
        assert conn.close.call_count == 0

    assert conn.close.call_count == 1


@patch("rabbit_consumer.openstack_api.OpenstackConnection")
def test_check_machine_exists_existing_machine(conn, vm_data):
    """
    Test that the function returns True when the machine exists
    """
    context = conn.return_value.__enter__.return_value
    context.compute.find_server.return_value = NonCallableMock()
    found = check_machine_exists(vm_data)

    conn.assert_called_once_with(vm_data.project_id)
    context.compute.find_server.assert_called_with(vm_data.virtual_machine_id)
    assert isinstance(found, bool) and found


@patch("rabbit_consumer.openstack_api.OpenstackConnection")
def test_check_machine_exists_deleted_machine(conn, vm_data):
    """
    Test that the function returns False when the machine does not exist
    """
    context = conn.return_value.__enter__.return_value
    context.compute.find_server.return_value = None
    found = check_machine_exists(vm_data)

    conn.assert_called_once_with(vm_data.project_id)
    context = conn.return_value.__enter__.return_value
    context.compute.find_server.assert_called_with(vm_data.virtual_machine_id)
    assert isinstance(found, bool) and not found


@patch("rabbit_consumer.openstack_api.OpenstackConnection")
@patch("rabbit_consumer.openstack_api.get_server_details")
def test_update_metadata(server_details, conn, vm_data):
    """
    Test that the function calls the correct functions to update the metadata on a VM
    """
    server_details.return_value = NonCallableMock()
    update_metadata(vm_data, {"key": "value"})

    server_details.assert_called_once_with(vm_data)

    conn.assert_called_once_with(vm_data.project_id)
    context = conn.return_value.__enter__.return_value
    context.compute.set_server_metadata.assert_called_once_with(
        server_details.return_value, {"key": "value"}
    )


@patch("rabbit_consumer.openstack_api.OpenstackConnection")
def test_get_server_details(conn, vm_data):
    """
    Test that the function calls the correct functions to get the details of a VM
    """
    context = conn.return_value.__enter__.return_value
    context.compute.servers.return_value = [NonCallableMock()]

    result = get_server_details(vm_data)

    context.compute.servers.assert_called_once_with(
        id=vm_data.virtual_machine_id, details=True
    )

    assert result == context.compute.servers.return_value[0]


@patch("rabbit_consumer.openstack_api.get_server_details")
@patch("rabbit_consumer.openstack_api.OpenstackAddress")
def test_get_server_networks(address, server_details, vm_data):
    """
    Test that the function calls the correct functions to get the networks of a VM
    """
    server_details.return_value = NonCallableMock()

    get_server_networks(vm_data)
    address.get_internal_networks.assert_called_once_with(
        server_details.return_value.addresses
    )
