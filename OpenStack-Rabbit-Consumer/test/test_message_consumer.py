from typing import List, Union, Dict
from unittest import mock
from unittest.mock import Mock, NonCallableMock, patch, call, MagicMock

import pytest

from rabbit_consumer.message_consumer import (
    is_aq_message,
    get_metadata_value,
    on_message,
    initiate_consumer,
    consume,
    convert_hostnames,
)
from rabbit_consumer.consumer_config import ConsumerConfig


# pylint: disable=duplicate-code
def _get_metadata_known_messages() -> List[str]:
    return [
        "AQ_DOMAIN",
        "AQ_SANDBOX",
        "AQ_OSVERSION",
        "AQ_PERSONALITY",
        "AQ_ARCHETYPE",
        "AQ_OS",
        "aq_domain",
        "aq_sandbox",
        "aq_osversion",
        "aq_personality",
        "aq_archetype",
        "aq_os",
    ]


@pytest.mark.parametrize("message", _get_metadata_known_messages())
def test_aq_messages_payload_metadata(message):
    rabbit_message = Mock()
    rabbit_message.get.return_value.get.return_value = {message: ""}

    assert is_aq_message(rabbit_message)


@pytest.mark.parametrize("message", _get_metadata_known_messages())
def test_aq_messages_payload_image_metadata(message):
    rabbit_message = Mock()
    rabbit_message.get.return_value.get.return_value = {message: ""}

    assert is_aq_message(rabbit_message)
    rabbit_message.get.assert_called_with("payload")
    rabbit_message.get.return_value.get.assert_called_with("metadata")


def test_aq_messages_unknown_message():
    rabbit_message = Mock()
    rabbit_message.get.return_value.get.return_value = {"unknown": ""}

    assert not is_aq_message(rabbit_message)
    rabbit_message.get.assert_called_with("payload")
    rabbit_message.get.return_value.get.assert_called_with("image_meta")


@pytest.mark.parametrize("key_name", ["metadata", "image_meta"])
def test_get_metadata_value(key_name):
    rabbit_message = Mock()
    mock_key = NonCallableMock()
    rabbit_message.get.return_value = {
        "metadata": {},
        "image_meta": {},
        key_name: {mock_key: "value"},
    }

    assert get_metadata_value(rabbit_message, mock_key) == "value"


@patch("rabbit_consumer.message_consumer.consume")
@patch("rabbit_consumer.message_consumer.json")
def test_on_message_parses_json(json, _):
    method = Mock()
    header = Mock()
    raw_body = Mock()

    on_message(method, header, raw_body)
    raw_body.decode.assert_called_once_with("utf-8")

    decoded_body = json.loads.return_value
    json.loads.assert_has_calls(
        [
            call(raw_body.decode.return_value),
            # Due to a bug in mocking the ["access"] triggers
            # a getitem call on the mock that's difficult to assert
            # pylint: disable=unnecessary-dunder-call
            call().__getitem__("oslo.message"),
            call(decoded_body.__getitem__.return_value),
        ],
        any_order=False,
    )


@patch("rabbit_consumer.message_consumer.consume")
@patch("rabbit_consumer.message_consumer.json")
def test_on_message_forwards_json_to_consumer(json, consume_mock):
    method = Mock()
    header = Mock()
    raw_body = Mock()

    on_message(method, header, raw_body)
    consume_mock.assert_called_once_with(json.loads.return_value)


@patch("rabbit_consumer.message_consumer.consume")
@patch("rabbit_consumer.message_consumer.json")
def test_on_message_exception_handling(_, consume_mock):
    method = Mock()
    header = Mock()
    raw_body = Mock()

    consume_mock.side_effect = Exception("test")
    on_message(method, header, raw_body)
    consume_mock.assert_called_once()


@patch("rabbit_consumer.message_consumer.rabbitpy")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
@patch("rabbit_consumer.message_consumer.verify_kerberos_ticket")
def test_initiate_consumer_config_elements(kerb, rabbit_conf, _):
    initiate_consumer()
    kerb.assert_called_once()
    rabbit_conf.config.get.assert_called_once_with("rabbit", "exchanges")


class MockedConfig(ConsumerConfig):
    rabbit_host = "rabbit_host"
    rabbit_port = 1234
    rabbit_username = "rabbit_username"
    rabbit_password = "rabbit_password"


@patch("rabbit_consumer.message_consumer.verify_kerberos_ticket")
@patch("rabbit_consumer.message_consumer.rabbitpy")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
def test_initiate_consumer_channel_setup(rabbit_conf, rabbitpy, _):
    exchanges = ["ex1", "ex2"]
    rabbit_conf.config.get.return_value.split.return_value = exchanges
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
    queue.bind.assert_has_calls(
        [call(exchange, routing_key="ral.info") for exchange in exchanges]
    )


@patch("rabbit_consumer.message_consumer.verify_kerberos_ticket")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
@patch("rabbit_consumer.message_consumer.on_message")
@patch("rabbit_consumer.message_consumer.rabbitpy")
def test_initiate_consumer_actual_consumption(rabbitpy, message_mock, _, __):
    queue_messages = [NonCallableMock(), NonCallableMock()]
    # We need our mocked queue to act like a generator
    rabbitpy.Queue.return_value.__iter__.return_value = queue_messages

    initiate_consumer()

    message_mock.assert_has_calls(
        [
            call(
                method=message.method, header=message.properties, raw_body=message.body
            )
            for message in queue_messages
        ]
    )

    for message in queue_messages:
        message.ack.assert_called_once()


@patch("rabbit_consumer.message_consumer.socket")
def test_convert_hostnames_multiple(socket):
    message = Mock()
    message.get.return_value = {"fixed_ips": [Mock(), Mock()]}
    socket.gethostbyaddr.side_effect = [["host1"], ["host2"]]

    hostnames = convert_hostnames(message, "")
    assert hostnames == ["host1", "host2"]


@patch("rabbit_consumer.message_consumer.socket")
def test_convert_hostnames_single(socket):
    message = Mock()
    message.get.return_value = {"fixed_ips": [Mock()]}
    socket.gethostbyaddr.side_effect = [["host1"]]

    hostnames = convert_hostnames(message, "")
    assert hostnames == ["host1"]


@patch("rabbit_consumer.message_consumer.socket")
def test_convert_hostnames_no_ips(_):
    message = Mock()
    message.get.return_value = {"fixed_ips": []}

    vm_name = "mocked_name"
    hostnames = convert_hostnames(message, vm_name)
    assert hostnames == [vm_name + ".novalocal"]


_FAKE_PAYLOAD = {
    "instance_id": NonCallableMock(),
    "display_name": "vm_display_name",
    "fixed_ips": [Mock(), Mock()],
    "metadata": MagicMock(),
    "host": NonCallableMock(),
    "vcpus": NonCallableMock(),
    "memory_mb": NonCallableMock(),
    "first_ip": [{"address": NonCallableMock()}],
}


def _message_get_create(arg_name: str) -> Union[str, Dict]:
    if arg_name == "event_type":
        return "compute.instance.create.end"
    if arg_name == "payload":
        return _FAKE_PAYLOAD
    return arg_name


@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.get_metadata_value")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.aq_api")
@patch("rabbit_consumer.message_consumer.ConsumerConfig")
def test_consume_create_machine_hostnames_good_path(
    app_conf, aq_api, openstack, hostname, get_metadata, _
):
    expected_hostnames = ["host1", "host2"]
    hostname.return_value = expected_hostnames

    message = Mock()
    message.get.side_effect = _message_get_create

    consume(message)
    aq_api.create_machine.assert_called_once_with(
        _FAKE_PAYLOAD["instance_id"],
        _FAKE_PAYLOAD["host"],
        _FAKE_PAYLOAD["vcpus"],
        _FAKE_PAYLOAD["memory_mb"],
        expected_hostnames[-1],
        app_conf.return_value.aq_prefix,
    )

    aq_api.add_machine_interface.assert_has_calls(
        [
            call(
                aq_api.create_machine.return_value,
                _FAKE_PAYLOAD["fixed_ips"][0].get.return_value,
                "eth0",
            ),
            call(
                aq_api.create_machine.return_value,
                _FAKE_PAYLOAD["fixed_ips"][1].get.return_value,
                "eth1",
            ),
        ]
    )

    aq_api.update_machine_interface.assert_called_once_with(
        aq_api.create_machine.return_value, "eth0"
    )

    aq_api.create_host.assert_called_once_with(
        expected_hostnames[0],
        aq_api.create_machine.return_value,
        get_metadata.return_value,
        _FAKE_PAYLOAD["fixed_ips"][0].get.return_value,
        get_metadata.return_value,
        get_metadata.return_value,
        get_metadata.return_value,
        get_metadata.return_value,
        get_metadata.return_value,
    )

    openstack.update_metadata.assert_has_calls(
        [
            # Where _context_project_id is the arg passed to message.get()
            call(
                "_context_project_id",
                _FAKE_PAYLOAD["instance_id"],
                {"HOSTNAMES": ", ".join(expected_hostnames)},
            ),
            call(
                "_context_project_id",
                _FAKE_PAYLOAD["instance_id"],
                {"AQ_MACHINENAME": aq_api.create_machine.return_value},
            ),
            call(
                "_context_project_id",
                _FAKE_PAYLOAD["instance_id"],
                {"AQ_STATUS": "SUCCESS"},
            ),
        ],
        any_order=False,
    )

    aq_api.aq_manage.assert_has_calls(
        [
            call(host, "sandbox", get_metadata.return_value)
            for host in expected_hostnames
        ]
    )
    aq_api.aq_make.assert_has_calls(
        [
            call(
                host,
                get_metadata.return_value,
                get_metadata.return_value,
                get_metadata.return_value,
                get_metadata.return_value,
            )
            for host in expected_hostnames
        ]
    )


@patch("rabbit_consumer.message_consumer.RabbitConsumer")
@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.openstack_api")
def test_consume_create_machine_update_metadata_failure(openstack, hostname, _, __):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create

    openstack.update_metadata.side_effect = Exception("mocked exception")

    with pytest.raises(Exception) as err:
        consume(message)
    assert str(err.value) == "Failed to update metadata"


@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_create_machine_aq_api_failure(aq_api, hostname, _, __, ___):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create

    aq_api.create_machine.side_effect = Exception("mocked exception")

    with pytest.raises(Exception) as err:
        consume(message)
    assert str(err.value) == "Failed to create machine: mocked exception"


@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_add_machine_interface_failure(aq_api, hostname, _, __, ___):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create

    aq_api.add_machine_interface.side_effect = Exception("mocked exception")

    with pytest.raises(Exception) as err:
        consume(message)
    assert "Failed to add machine interface" in str(err.value)
    assert "mocked exception" in str(err.value)


@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_add_machine_interface_address_failure(aq_api, hostname, _, __, ___):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create

    aq_api.add_machine_interface_address.side_effect = Exception("mocked exception")

    with pytest.raises(Exception) as err:
        consume(message)
    assert "Failed to add machine interface address" in str(err.value)
    assert "mocked exception" in str(err.value)


@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_update_machine_interface_failure(aq_api, hostname, _, __, ___):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create

    aq_api.update_machine_interface.side_effect = Exception("mocked exception")

    with pytest.raises(Exception) as err:
        consume(message)
    assert "Failed to set default interface" in str(err.value)
    assert "mocked exception" in str(err.value)


@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_create_host_failure(aq_api, hostname, _, __, ___):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create

    vm_name = "vm-openstack-AbC-123"
    aq_api.create_host.side_effect = Exception(vm_name)

    with pytest.raises(Exception) as err:
        consume(message)

    assert "IP Address already exists on" in str(err.value)
    assert vm_name in str(err.value)


@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_aq_manage_failure_marks_aq_failed(aq_api, hostname, openstack, __, ___):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create
    aq_api.aq_manage.side_effect = Exception("mocked_exception")

    with pytest.raises(Exception) as err:
        consume(message)

    openstack.update_metadata.assert_called_with(
        "_context_project_id", _FAKE_PAYLOAD["instance_id"], {"AQ_STATUS": "FAILED"}
    )
    assert "Failed to set Aquilon configuration" in str(err.value)


@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_aq_make_failure_marks_aq_failed(aq_api, hostname, openstack, __, ___):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create
    aq_api.aq_make.side_effect = Exception("mocked_exception")

    with pytest.raises(Exception) as err:
        consume(message)

    openstack.update_metadata.assert_called_with(
        "_context_project_id", _FAKE_PAYLOAD["instance_id"], {"AQ_STATUS": "FAILED"}
    )
    assert "Failed to set Aquilon configuration" in str(err.value)


_DELETE_FAKE_PAYLOAD = {
    "instance_id": NonCallableMock(),
    "metadata": {"AQ_MACHINENAME": "AQ-HOST1", "HOSTNAMES": "host1,host2"},
}


def _message_get_delete(arg_name: str) -> Union[str, Dict]:
    if arg_name == "event_type":
        return "compute.instance.delete.start"
    if arg_name == "payload":
        return _DELETE_FAKE_PAYLOAD
    return arg_name


@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_delete_machine_good_path(aq_api, _):
    message = Mock()
    message.get.side_effect = _message_get_delete

    consume(message)

    aq_api.delete_host.assert_has_calls([call("host1"), call("host2")], any_order=True)
    aq_api.del_machine_interface_address.assert_has_calls(
        [
            call("host1", "eth0", _DELETE_FAKE_PAYLOAD["metadata"]["AQ_MACHINENAME"]),
            call("host2", "eth0", _DELETE_FAKE_PAYLOAD["metadata"]["AQ_MACHINENAME"]),
        ]
    )

    aq_api.delete_machine.assert_called_once_with(
        _DELETE_FAKE_PAYLOAD["metadata"]["AQ_MACHINENAME"]
    )

    aq_api.reset_env.assert_has_calls([call("host1"), call("host2")], any_order=True)


@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_delete_machine_aq_host_delete_failure(aq_api, openstack_api, __):
    message = Mock()
    message.get.side_effect = _message_get_delete

    aq_api.delete_host.side_effect = Exception("mocked exception")
    with pytest.raises(Exception) as err:
        consume(message)

    openstack_api.update_metadata.assert_called_with(
        "_context_project_id",
        _DELETE_FAKE_PAYLOAD["instance_id"],
        {"AQ_STATUS": "FAILED"},
    )
    assert "Failed to delete host" in str(err.value)


@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_delete_machine_aq_del_machine_interface_address(aq_api, _):
    message = Mock()
    message.get.side_effect = _message_get_delete

    aq_api.del_machine_interface_address.side_effect = Exception("mocked exception")
    with pytest.raises(Exception) as err:
        consume(message)
    assert "Failed to delete interface address" in str(err.value)


@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_delete_machine_aq_delete_machine_failure(aq_api, _):
    message = Mock()
    message.get.side_effect = _message_get_delete

    aq_api.delete_machine.side_effect = Exception("mocked exception")
    with pytest.raises(Exception) as err:
        consume(message)
    assert "Failed to delete machine" in str(err.value)


@patch("rabbit_consumer.message_consumer.is_aq_message")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_delete_machine_aq_reset_env_failure(aq_api, openstack_api, _):
    message = Mock()
    message.get.side_effect = _message_get_delete

    aq_api.reset_env.side_effect = Exception("mocked exception")
    with pytest.raises(Exception) as err:
        consume(message)
    openstack_api.update_metadata.assert_called_with(
        "_context_project_id",
        _DELETE_FAKE_PAYLOAD["instance_id"],
        {"AQ_STATUS": "FAILED"},
    )
    assert "Failed to reset Aquilon configuration" in str(err.value)
