from unittest.mock import Mock, NonCallableMock, patch, call

import pytest

# noinspection PyUnresolvedReferences
# pylint: disable=unused-import
from fixtures import (
    fixture_rabbit_message,
    fixture_vm_data,
    fixture_openstack_address_list,
    fixture_openstack_address,
    fixture_image_metadata,
)
from rabbit_consumer.consumer_config import ConsumerConfig
from rabbit_consumer.message_consumer import (
    on_message,
    initiate_consumer,
    add_hostname_to_metadata,
    handle_create_machine,
    handle_machine_delete,
    SUPPORTED_MESSAGE_TYPES,
)


@pytest.fixture(name="valid_event_type")
def fixture_valid_event_type():
    """
    Fixture for a valid event type
    """
    mock = NonCallableMock()
    mock.event_type = SUPPORTED_MESSAGE_TYPES["create"]
    return mock


@patch("rabbit_consumer.message_consumer.consume")
@patch("rabbit_consumer.message_consumer.MessageEventType")
@patch("rabbit_consumer.message_consumer.RabbitMessage")
def test_on_message_parses_json(
    message_parser, message_event_type, consume, valid_event_type
):
    """
    Test that the function parses the message body as JSON
    """
    message_event_type.from_json.return_value = valid_event_type

    with (
        patch("rabbit_consumer.message_consumer.json") as json,
        patch("rabbit_consumer.message_consumer.is_aq_managed_image"),
    ):
        message = Mock()
        on_message(message)

    decoded_body = json.loads.return_value
    message_parser.from_json.assert_called_once_with(decoded_body["oslo.message"])
    consume.assert_called_once_with(message_parser.from_json.return_value)
    message.ack.assert_called_once()


@patch("rabbit_consumer.message_consumer.consume")
@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.MessageEventType")
def test_on_message_ignores_wrong_message_type(message_event_type, is_managed, consume):
    """
    Test that the function ignores messages with the wrong message type
    """
    message_event = NonCallableMock()
    message_event.event_type = "wrong"
    message_event_type.from_json.return_value = message_event

    with patch("rabbit_consumer.message_consumer.json"):
        message = Mock()
        on_message(message)

    is_managed.assert_not_called()
    consume.assert_not_called()
    message.ack.assert_called_once()


@pytest.mark.parametrize("event_type", SUPPORTED_MESSAGE_TYPES.values())
@patch("rabbit_consumer.message_consumer.consume")
@patch("rabbit_consumer.message_consumer.MessageEventType")
def test_on_message_accepts_event_types(message_event_type, consume, event_type):
    """
    Test that the function accepts the correct event types
    """
    message_event = NonCallableMock()
    message_event.event_type = event_type
    message_event_type.from_json.return_value = message_event

    with (
        patch("rabbit_consumer.message_consumer.RabbitMessage"),
        patch("rabbit_consumer.message_consumer.json"),
        patch("rabbit_consumer.message_consumer.is_aq_managed_image") as is_managed,
    ):
        is_managed.return_value = True
        message = Mock()
        on_message(message)

    is_managed.assert_called_once()
    consume.assert_called_once()
    message.ack.assert_called_once()


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.consume")
def test_on_message_ignores_non_aq(consume_mock, aq_message_mock, valid_event_type):
    """
    Test that the function ignores non-AQ messages and acks them
    """
    message = Mock()
    aq_message_mock.return_value = False

    with (
        patch("rabbit_consumer.message_consumer.json"),
        patch("rabbit_consumer.message_consumer.RabbitMessage"),
        patch(
            "rabbit_consumer.message_consumer.MessageEventType"
        ) as message_event_type,
    ):
        message_event_type.from_json.return_value = valid_event_type
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
        vm_data, {"HOSTNAMES": ",".join(hostnames), "AQ_STATUS": "SUCCESS"}
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


@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.aq_api")
@patch("rabbit_consumer.message_consumer.add_hostname_to_metadata")
# pylint: disable=too-many-arguments
def test_consume_create_machine_hostnames_good_path(
    metadata, aq_api, openstack, rabbit_message, valid_event_type, image_metadata
):
    """
    Test that the function calls the correct functions in the correct order to register a new machine
    """
    with (
        patch("rabbit_consumer.message_consumer.VmData") as data_patch,
        patch("rabbit_consumer.message_consumer.is_aq_managed_image") as is_managed,
        patch("rabbit_consumer.message_consumer.MessageEventType") as message_type,
    ):
        is_managed.return_value = image_metadata
        message_type.from_json.return_value = valid_event_type

        handle_create_machine(rabbit_message)

        vm_data = data_patch.from_message.return_value
        network_details = openstack.get_server_networks.return_value

    data_patch.from_message.assert_called_with(rabbit_message)
    openstack.get_server_networks.assert_called_with(vm_data)

    # Check main Aq Flow
    aq_api.create_machine.assert_called_once_with(rabbit_message, vm_data)
    machine_name = aq_api.create_machine.return_value

    # Networking
    aq_api.add_machine_nics.assert_called_once_with(machine_name, network_details)

    aq_api.set_interface_bootable.assert_called_once_with(machine_name, "eth0")

    aq_api.create_host.assert_called_once_with(
        image_metadata, network_details, machine_name
    )
    aq_api.aq_manage.assert_called_once_with(network_details, image_metadata)
    aq_api.aq_make.assert_called_once_with(network_details, image_metadata)

    # Metadata
    metadata.assert_called_once_with(vm_data, network_details)


@patch("rabbit_consumer.message_consumer.delete_machine")
def test_consume_delete_machine_good_path(
    delete_machine, rabbit_message, openstack_address_list
):
    """
    Test that the function calls the correct functions in the correct order to delete a machine
    """
    rabbit_message.payload.metadata.machine_name = "AQ-HOST1"

    with (
        patch("rabbit_consumer.message_consumer.VmData") as data_patch,
        patch("rabbit_consumer.message_consumer.openstack_api") as openstack,
    ):
        openstack.get_server_networks.return_value = openstack_address_list

        handle_machine_delete(rabbit_message)

        data_patch.from_message.assert_called_with(rabbit_message)
        openstack.get_server_networks.assert_called_with(
            data_patch.from_message.return_value
        )

    delete_machine.assert_called_once_with(addresses=openstack_address_list)
