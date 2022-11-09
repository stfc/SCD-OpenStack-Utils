from typing import List
from unittest import mock
from unittest.mock import Mock, NonCallableMock, patch, call

import pytest

from rabbit_consumer.message_consumer import (
    is_aq_message,
    get_metadata_value,
    on_message,
    initiate_consumer,
)


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


def _get_image_metadata_known_messages() -> List[str]:
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


@pytest.mark.parametrize("message", _get_image_metadata_known_messages())
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
    channel = Mock()
    method = Mock()
    header = Mock()
    raw_body = Mock()

    on_message(channel, method, header, raw_body)
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
def test_on_message_forwards_json_to_consumer(json, consume):
    channel = Mock()
    method = Mock()
    header = Mock()
    raw_body = Mock()

    on_message(channel, method, header, raw_body)
    consume.assert_called_once_with(json.loads.return_value)
    channel.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)


@patch("rabbit_consumer.message_consumer.consume")
@patch("rabbit_consumer.message_consumer.json")
def test_on_message_exception_handling(_, consume):
    channel = Mock()
    method = Mock()
    header = Mock()
    raw_body = Mock()

    consume.side_effect = Exception("test")
    on_message(channel, method, header, raw_body)
    consume.assert_called_once()
    channel.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)


@patch("rabbit_consumer.message_consumer.pika")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
def test_initiate_consumer_config_elements(rabbit_conf, _):
    initiate_consumer()
    rabbit_conf.config.get.assert_has_calls(
        [
            call("aquilon", "prefix"),
            call("rabbit", "host"),
            call("rabbit", "login_user"),
            call("rabbit", "login_pass"),
            call("rabbit", "exchanges"),
        ],
        any_order=True,
    )

    rabbit_conf.config.getint.assert_called_with("rabbit", "port")


@patch("rabbit_consumer.message_consumer.pika")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
def test_initiate_consumer_channel_setup(rabbit_conf, pika):
    exchanges = ["ex1", "ex2"]
    rabbit_conf.config.get.return_value.split.return_value = exchanges
    initiate_consumer()

    pika.PlainCredentials.assert_called_once_with(
        rabbit_conf.config.get.return_value, rabbit_conf.config.get.return_value
    )

    pika.ConnectionParameters.assert_called_once_with(
        rabbit_conf.config.get.return_value,
        rabbit_conf.config.getint.return_value,
        "/",
        pika.PlainCredentials.return_value,
        connection_attempts=mock.ANY,
        retry_delay=mock.ANY,
    )

    pika.BlockingConnection.assert_called_once_with(
        pika.ConnectionParameters.return_value
    )

    channel = pika.BlockingConnection.return_value.channel.return_value
    channel.queue_declare.assert_called_once_with("ral.info")
    channel.queue_bind.assert_has_calls(
        [call("ral.info", i, "ral.info") for i in exchanges]
    )


@patch("rabbit_consumer.message_consumer.pika")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
def test_initiate_consumer_actual_consumption(_, pika):
    initiate_consumer()
    channel = pika.BlockingConnection.return_value.channel.return_value
    channel.basic_consume.assert_called_once_with(on_message, "ral.info")

    channel.start_consuming.assert_called_once()


@patch("rabbit_consumer.message_consumer.pika")
@patch("rabbit_consumer.message_consumer.RabbitConsumer")
def test_initiate_consumer_consumption_exception(_, pika):
    channel = pika.BlockingConnection.return_value.channel.return_value
    channel.start_consuming.side_effect = Exception("test")

    with pytest.raises(Exception) as err:
        initiate_consumer()

    assert err.value.args[0] == "test"

    channel.start_consuming.assert_called_once()
    connection = pika.BlockingConnection.return_value
    connection.close.assert_called_once()


@patch("rabbit_consumer.message_consumer.RabbitConsumer")
@patch("rabbit_consumer.message_consumer.sys.exit")
@patch("rabbit_consumer.message_consumer.pika")
def test_initiate_consumer_keyboard_interrupt(pika, sys_exit, _):
    channel = pika.BlockingConnection.return_value.channel.return_value
    channel.start_consuming.side_effect = KeyboardInterrupt()

    initiate_consumer()

    channel.stop_consuming.assert_called_once()
    connection = pika.BlockingConnection.return_value
    connection.close.assert_called_once()
    sys_exit.assert_called_once_with(0)
