from unittest.mock import Mock, NonCallableMock, patch, call, MagicMock

import pytest

# noinspection PyUnresolvedReferences
# pylint: disable=unused-import
from fixtures import (
    fixture_rabbit_message,
    fixture_vm_data,
    fixture_openstack_address_list,
    fixture_openstack_address,
)
from rabbit_consumer.consumer_config import ConsumerConfig
from rabbit_consumer.message_consumer import (
    is_aq_managed_image,
    on_message,
    initiate_consumer,
    add_hostname_to_metadata,
    handle_create_machine,
    handle_machine_delete,
)


@pytest.mark.parametrize(
    "image_name",
    [
        "rocky-8-aq",
        "centos-7-aq",
        "scientificlinux-7-aq",
        "scientificlinux-7-nogui",
        "warehoused-scientificlinux-7-aq-23-01-2023-14-49-18",
        "warehoused-centos-7-aq-23-01-2023-14-49-18",
        "warehoused-rocky-8-aq-26-01-2023-09-21-12",
    ],
)
def test_is_aq_managed_image_with_real_aq_image_names(image_name, rabbit_message):
    """
    Test that the function returns True for AQ managed images based on some example image names
    """
    rabbit_message.payload.image_name = image_name
    assert is_aq_managed_image(rabbit_message)


def test_aq_messages_no_image_name(rabbit_message):
    """
    Test that the function returns False for messages without an image name
    """
    rabbit_message.payload.image_name = None
    assert not is_aq_managed_image(rabbit_message)


@pytest.mark.parametrize(
    "image_name",
    [
        "image-name",
        "rhel-8",
        "test",
        "ubuntu",
        "capi",
        "warehoused-ubuntu-focal-20.04-gui-08-03-2022-13-39-19",
        "Fedora-Atomic-FINAL",
        "capi-ubuntu-2004-kube-v1.23.15-2023-03-14",
    ],
)
def test_aq_messages_other_image_names(image_name, rabbit_message):
    """
    Test that the function returns False for messages with non-AQ image names
    """
    rabbit_message.payload.image_name = image_name
    assert not is_aq_managed_image(rabbit_message)


@patch("rabbit_consumer.message_consumer.consume")
@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.json")
@patch("rabbit_consumer.message_consumer.RabbitMessage")
def test_on_message_parses_json(message_parser, json, is_managed, consume):
    """
    Test that the function parses the message body as JSON
    """
    message = Mock()
    is_managed.return_value = True
    json.loads.return_value = {
        "oslo.message": {"event_type": "compute.instance.create.end"}
    }

    on_message(message)

    raw_body = message.body
    raw_body.decode.assert_called_once_with("utf-8")

    decoded_body = json.loads.return_value
    message_parser.from_json.assert_called_once_with(decoded_body["oslo.message"])
    consume.assert_called_once_with(message_parser.from_json.return_value)
    message.ack.assert_called_once()


@patch("rabbit_consumer.message_consumer.consume")
@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.json")
def test_on_message_ignores_wrong_message_type(json, is_managed, consume):
    """
    Test that the function ignores messages with the wrong message type
    """
    message = Mock()
    json.loads.return_value = {"oslo.message": {"event_type": "wrong"}}

    on_message(message)

    is_managed.assert_not_called()
    consume.assert_not_called()
    message.ack.assert_called_once()


@pytest.mark.parametrize(
    "event_type", ["compute.instance.create.end", "compute.instance.delete.start"]
)
@patch("rabbit_consumer.message_consumer.consume")
@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.json")
def test_on_message_accepts_event_types(json, is_managed, consume, event_type):
    """
    Test that the function accepts the correct event types
    """
    message = Mock()
    json.loads.return_value = {"oslo.message": {"event_type": event_type}}
    is_managed.return_value = True

    with patch("rabbit_consumer.message_consumer.RabbitMessage"):
        on_message(message)

    is_managed.assert_called_once()
    consume.assert_called_once()
    message.ack.assert_called_once()


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.consume")
@patch("rabbit_consumer.message_consumer.json")
def test_on_message_ignores_non_aq(json, consume_mock, aq_message_mock):
    """
    Test that the function ignores non-AQ messages and acks them
    """
    message = Mock()
    aq_message_mock.return_value = False
    json.loads.return_value = {
        "oslo.message": {"event_type": "compute.instance.create.end"}
    }

    with patch("rabbit_consumer.message_consumer.RabbitMessage"):
        on_message(message)

    aq_message_mock.assert_called_once()
    consume_mock.assert_not_called()
    message.ack.assert_called_once()


# pylint: disable=too-few-public-methods
class MockedConfig(ConsumerConfig):
    """
    Provides a mocked input config for the consumer
    """

    rabbit_host = "rabbit_host"
    rabbit_port = 1234
    rabbit_username = "rabbit_username"
    rabbit_password = "rabbit_password"


@patch("rabbit_consumer.message_consumer.verify_kerberos_ticket")
@patch("rabbit_consumer.message_consumer.rabbitpy")
def test_initiate_consumer_channel_setup(rabbitpy, _):
    """
    Test that the function sets up the channel and queue correctly
    """
    mocked_config = MockedConfig()

    with patch("rabbit_consumer.message_consumer.ConsumerConfig") as config:
        config.return_value = mocked_config
        initiate_consumer()

    rabbitpy.Connection.assert_called_once_with(
        f"amqp://{mocked_config.rabbit_username}:{mocked_config.rabbit_password}@{mocked_config.rabbit_host}:{mocked_config.rabbit_port}/"
    )

    connection = rabbitpy.Connection.return_value.__enter__.return_value
    connection.channel.assert_called_once()
    channel = connection.channel.return_value.__enter__.return_value

    rabbitpy.Queue.assert_called_once_with(channel, name="ral.info", durable=True)
    queue = rabbitpy.Queue.return_value
    queue.bind.assert_called_once_with("nova", routing_key="ral.info")


@patch("rabbit_consumer.message_consumer.verify_kerberos_ticket")
@patch("rabbit_consumer.message_consumer.on_message")
@patch("rabbit_consumer.message_consumer.rabbitpy")
def test_initiate_consumer_actual_consumption(rabbitpy, message_mock, _):
    """
    Test that the function actually consumes messages
    """
    queue_messages = [NonCallableMock(), NonCallableMock()]
    # We need our mocked queue to act like a generator
    rabbitpy.Queue.return_value.__iter__.return_value = queue_messages

    initiate_consumer()

    message_mock.assert_has_calls([call(message) for message in queue_messages])


@patch("rabbit_consumer.message_consumer.openstack_api")
def test_add_hostname_to_metadata_machine_exists(
    openstack_api, vm_data, openstack_address_list
):
    """
    Test that the function adds the hostname to the metadata when the machine exists
    """
    openstack_api.check_machine_exists.return_value = True
    add_hostname_to_metadata(vm_data, openstack_address_list)

    openstack_api.check_machine_exists.assert_called_once_with(vm_data)
    hostnames = [i.hostname for i in openstack_address_list]
    openstack_api.update_metadata.assert_called_with(
        vm_data, {"HOSTNAMES": ",".join(hostnames)}
    )


@patch("rabbit_consumer.message_consumer.openstack_api")
def test_add_hostname_to_metadata_machine_does_not_exist(openstack_api, vm_data):
    """
    Test that the function does not add the hostname to the metadata when the machine does not exist
    """
    openstack_api.check_machine_exists.return_value = False
    add_hostname_to_metadata(vm_data, [])

    openstack_api.check_machine_exists.assert_called_once_with(vm_data)
    openstack_api.update_metadata.assert_not_called()


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.aq_api")
@patch("rabbit_consumer.message_consumer.add_hostname_to_metadata")
def test_consume_create_machine_hostnames_good_path(
    metadata, aq_api, openstack, is_managed, rabbit_message
):
    """
    Test that the function calls the correct functions in the correct order to register a new machine
    """
    with patch("rabbit_consumer.message_consumer.VmData") as data_patch:
        handle_create_machine(rabbit_message)

        vm_data = data_patch.from_message.return_value
        network_details = openstack.get_server_networks.return_value
        os_details = is_managed.return_value

    data_patch.from_message.assert_called_with(rabbit_message)
    openstack.get_server_networks.assert_called_with(vm_data)

    # Check main Aq Flow
    aq_api.create_machine.assert_called_once_with(rabbit_message, vm_data)
    machine_name = aq_api.create_machine.return_value

    # Networking
    aq_api.add_machine_nics.assert_called_once_with(machine_name, network_details)

    aq_api.set_interface_bootable.assert_called_once_with(machine_name, "eth0")

    aq_api.create_host.assert_called_once_with(
        os_details, network_details, machine_name
    )
    aq_api.aq_manage.assert_called_once_with(network_details)
    aq_api.aq_make.assert_called_once_with(network_details, os_details)

    # Metadata
    metadata.assert_called_once_with(vm_data, network_details)
    openstack.update_metadata.assert_called_once_with(vm_data, {"AQ_STATUS": "SUCCESS"})


@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_delete_machine_good_path(aq_api, rabbit_message):
    """
    Test that the function calls the correct functions in the correct order to delete a machine
    """
    rabbit_message.payload.metadata.machine_name = "AQ-HOST1"
    mock_network_data = [NonCallableMock(), NonCallableMock()]

    with (
        patch("rabbit_consumer.message_consumer.VmData") as data_patch,
        patch("rabbit_consumer.message_consumer.openstack_api") as openstack_patch,
    ):
        openstack_patch.get_server_networks.return_value = mock_network_data

        handle_machine_delete(rabbit_message)

        data_patch.from_message.assert_called_with(rabbit_message)
        openstack_patch.get_server_networks.assert_called_with(
            data_patch.from_message.return_value
        )

    aq_api.delete_host.assert_has_calls(
        [call(i.hostname) for i in mock_network_data], any_order=True
    )

    aq_api.delete_machine.assert_called_once_with(
        rabbit_message.payload.metadata.machine_name
    )
