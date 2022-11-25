from unittest.mock import patch, NonCallableMock

import pytest

from rabbit_consumer.common import RabbitConsumer


def test_get_env_str():
    with patch.dict("os.environ", {"TEST_VAR": "test_value"}):
        assert RabbitConsumer.get_env_str("TEST_VAR") == "test_value"


def test_get_env_int():
    with patch.dict("os.environ", {"TEST_VAR": "1"}):
        assert RabbitConsumer.get_env_int("TEST_VAR") == 1


@patch("rabbit_consumer.common.ConfigParser")
def test_get_config_key(config_parser):
    RabbitConsumer.reset()
    config_parser.assert_not_called()

    key_name = NonCallableMock()
    returned = RabbitConsumer.config[key_name]

    config_handle = config_parser.return_value
    config_handle.read.assert_called_once_with("/usr/src/app/consumer.ini")

    config_handle.__getitem__.assert_called_once_with(key_name)
    assert returned == config_handle.__getitem__.return_value


@patch("rabbit_consumer.common.ConfigParser")
def test_get_config_parsed_correct_number_of_times(config_parser):
    RabbitConsumer.reset()
    config_parser.assert_not_called()
    config_handle = config_parser.return_value.read

    RabbitConsumer.get_config()
    RabbitConsumer.get_config()
    config_handle.assert_called_once()

    RabbitConsumer.reset()
    RabbitConsumer.get_config()
    # Two resets == two config parse times
    assert config_handle.call_count == 2


@pytest.mark.parametrize("exception", [IOError, SystemError, RuntimeError])
@patch("rabbit_consumer.common.ConfigParser")
def test_load_config_throw_logs(config, exception):
    RabbitConsumer.reset()
    config.side_effect = exception()

    with pytest.raises(exception):
        RabbitConsumer.get_config()
