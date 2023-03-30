from typing import Union, Dict
from unittest.mock import Mock, NonCallableMock, patch, call, MagicMock

import pytest

from rabbit_consumer.aq_fields import AqFields
from rabbit_consumer.consumer_config import ConsumerConfig
from rabbit_consumer.message_consumer import (
    is_aq_managed_image,
    get_metadata_value,
    on_message,
    initiate_consumer,
    consume,
    convert_hostnames,
)


@pytest.mark.parametrize(
    "image_name",
    [
        "rocky-8-aq",
        "rocky8-raw",
        "centos-7-aq",
        "scientificlinux-7-aq",
        "scientificlinux-7-nogui",
        "warehoused-scientificlinux-7-aq-23-01-2023-14-49-18",
        "warehoused-centos-7-aq-23-01-2023-14-49-18",
        "warehoused-rocky-8-aq-26-01-2023-09-21-12",
    ],
)
def test_is_aq_managed_image_with_real_aq_image_names(image_name):
    message = {"payload": {"image_name": image_name}}
    assert is_aq_managed_image(message)


def test_aq_messages_no_payload():
    message = {"image_name": {}}
    assert not is_aq_managed_image(message)


def test_aq_messages_no_image_name():
    message = {"payload": {"image_name": {}}}
    assert not is_aq_managed_image(message)


def test_aq_messages_no_payload_no_image_name():
    message = {}
    assert not is_aq_managed_image(message)


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
def test_aq_messages_other_image_names(image_name):
    message = {"payload": {"image_name": image_name}}
    assert not is_aq_managed_image(message)


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
@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.json")
def test_on_message_parses_json(json, aq_message, _):
    message = MagicMock()
    raw_body = message.body
    aq_message.return_value = True

    on_message(message)
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
@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.json")
def test_on_message_forwards_json_to_consumer(json, aq_message_mock, consume_mock):
    message = Mock()
    aq_message_mock.return_value = True

    on_message(message)
    aq_message_mock.assert_called_once_with(json.loads.return_value)
    consume_mock.assert_called_once_with(json.loads.return_value)
    message.ack.assert_called_once()


@patch("rabbit_consumer.message_consumer.consume")
@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.json")
def test_on_message_ignores_non_aq(json, aq_message_mock, consume_mock):
    message = Mock()
    aq_message_mock.return_value = False

    on_message(message)

    aq_message_mock.assert_called_once_with(json.loads.return_value)
    consume_mock.assert_not_called()
    message.ack.assert_not_called()


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
    queue_messages = [NonCallableMock(), NonCallableMock()]
    # We need our mocked queue to act like a generator
    rabbitpy.Queue.return_value.__iter__.return_value = queue_messages

    initiate_consumer()

    message_mock.assert_has_calls([call(message) for message in queue_messages])


@patch("rabbit_consumer.message_consumer.socket")
def test_convert_hostnames_multiple(socket):
    message = Mock()
    message.get.return_value = {"fixed_ips": [Mock(), Mock()]}
    socket.gethostbyaddr.side_effect = [["host1"], ["host2"]]

    hostnames = convert_hostnames(message)
    assert hostnames == ["host1", "host2"]


@patch("rabbit_consumer.message_consumer.socket")
def test_convert_hostnames_single(socket):
    message = Mock()
    message.get.return_value = {"fixed_ips": [Mock()]}
    socket.gethostbyaddr.side_effect = [["host1"]]

    hostnames = convert_hostnames(message)
    assert hostnames == ["host1"]


@patch("rabbit_consumer.message_consumer.socket")
def test_convert_hostnames_no_ips(_):
    message = Mock()
    message.get.return_value = {"fixed_ips": []}

    hostnames = convert_hostnames(message)
    assert not hostnames


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


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
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
        message,
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
        _FAKE_PAYLOAD["fixed_ips"][0].get.return_value,
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
            call(host, "domain", app_conf.return_value.aq_domain)
            for host in expected_hostnames
        ]
    )

    expected_fields = AqFields(
        archetype=get_metadata.return_value,
        hostnames=expected_hostnames,
        osname=get_metadata.return_value,
        osversion=get_metadata.return_value,
        personality=get_metadata.return_value,
        project_id="_context_project_id",
    )

    aq_api.aq_make.assert_has_calls(
        [call(host, expected_fields) for host in expected_hostnames]
    )


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.openstack_api")
def test_consume_create_machine_update_metadata_failure(openstack, hostname, _):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create

    openstack.update_metadata.side_effect = Exception("mocked exception")

    with pytest.raises(Exception) as err:
        consume(message)
    assert str(err.value) == "Failed to update metadata"


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_create_machine_aq_api_failure(aq_api, hostname, _, __):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create

    aq_api.create_machine.side_effect = Exception("mocked exception")

    with pytest.raises(Exception) as err:
        consume(message)
    assert str(err.value) == "Failed to create machine"


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_add_machine_interface_failure(aq_api, hostname, _, __):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create

    aq_api.add_machine_interface.side_effect = Exception("mocked exception")

    with pytest.raises(Exception) as err:
        consume(message)
    assert "Failed to add machine interface" in str(err.value)


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_add_machine_interface_address_failure(aq_api, hostname, _, __):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create

    aq_api.add_machine_interface_address.side_effect = Exception("mocked exception")

    with pytest.raises(Exception) as err:
        consume(message)
    assert "Failed to add machine interface address" in str(err.value)


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_update_machine_interface_failure(aq_api, hostname, _, __):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create

    aq_api.update_machine_interface.side_effect = Exception("mocked exception")

    with pytest.raises(Exception) as err:
        consume(message)
    assert "Failed to set default interface" in str(err.value)


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_aq_manage_failure_marks_aq_failed(aq_api, hostname, openstack, __):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create
    aq_api.aq_manage.side_effect = Exception("mocked_exception")

    with pytest.raises(Exception):
        consume(message)

    openstack.update_metadata.assert_called_with(
        "_context_project_id", _FAKE_PAYLOAD["instance_id"], {"AQ_STATUS": "FAILED"}
    )


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.convert_hostnames")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_aq_make_failure_marks_aq_failed(aq_api, hostname, openstack, _):
    hostname.return_value = ["host1", "host2"]

    message = Mock()
    message.get.side_effect = _message_get_create
    aq_api.aq_make.side_effect = Exception("mocked_exception")

    with pytest.raises(Exception):
        consume(message)

    openstack.update_metadata.assert_called_with(
        "_context_project_id", _FAKE_PAYLOAD["instance_id"], {"AQ_STATUS": "FAILED"}
    )


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


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_delete_machine_good_path(aq_api, _):
    message = Mock()
    message.get.side_effect = _message_get_delete

    consume(message)

    aq_api.delete_host.assert_has_calls([call("host1"), call("host2")], any_order=True)
    aq_api.delete_machine.assert_called_once_with(
        _DELETE_FAKE_PAYLOAD["metadata"]["AQ_MACHINENAME"]
    )


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.openstack_api")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_delete_machine_aq_host_delete_failure(aq_api, openstack_api, __):
    message = Mock()
    message.get.side_effect = _message_get_delete

    aq_api.delete_host.side_effect = ConnectionError("mocked exception")
    consume(message)

    openstack_api.update_metadata.assert_called_with(
        "_context_project_id",
        _DELETE_FAKE_PAYLOAD["instance_id"],
        {"AQ_STATUS": "FAILED"},
    )


@patch("rabbit_consumer.message_consumer.is_aq_managed_image")
@patch("rabbit_consumer.message_consumer.aq_api")
def test_consume_delete_machine_aq_delete_machine_failure(aq_api, _):
    message = Mock()
    message.get.side_effect = _message_get_delete

    aq_api.delete_machine.side_effect = Exception("mocked exception")
    with pytest.raises(Exception):
        consume(message)
