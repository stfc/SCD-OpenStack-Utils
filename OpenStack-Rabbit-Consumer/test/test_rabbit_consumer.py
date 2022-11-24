from unittest.mock import patch, NonCallableMock

import pytest

from rabbit_consumer.rabbit_consumer import RabbitConsumer, ConsumerConfig

AQ_FIELDS = [
    ("aq_archetype", "AQ_ARCHETYPE"),
    ("aq_domain", "AQ_DOMAIN"),
    ("aq_personality", "AQ_PERSONALITY"),
    ("aq_prefix", "AQ_PREFIX"),
    ("aq_url", "AQ_URL"),
]

OPENSTACK_FIELDS = [
    ("openstack_auth_url", "OPENSTACK_AUTH_URL"),
    ("openstack_ca_cert", "OPENSTACK_CA_CERT"),
    ("openstack_compute_url", "OPENSTACK_COMPUTE_URL"),
    ("openstack_domain_name", "OPENSTACK_DOMAIN_NAME"),
    ("openstack_project_id", "OPENSTACK_PROJECT_ID"),
    ("openstack_username", "OPENSTACK_USERNAME"),
    ("openstack_password", "OPENSTACK_PASSWORD"),
]

RABBIT_FIELDS = [
    ("rabbit_host", "RABBIT_HOST"),
    ("rabbit_port", "RABBIT_PORT"),
    ("rabbit_username", "RABBIT_USERNAME"),
    ("rabbit_password", "RABBIT_PASSWORD"),
]


@pytest.mark.parametrize(
    "config_name,env_var", AQ_FIELDS + OPENSTACK_FIELDS + RABBIT_FIELDS
)
def test_config_gets_os_env_vars(monkeypatch, config_name, env_var):
    expected = "MOCK_ENV"
    monkeypatch.setenv(env_var, expected)
    assert getattr(ConsumerConfig(), config_name) == expected


@patch("rabbit_consumer.rabbit_consumer.ConfigParser")
def test_get_config_key(config_parser):
    RabbitConsumer.reset()
    config_parser.assert_not_called()

    key_name = NonCallableMock()
    returned = RabbitConsumer.config[key_name]

    config_handle = config_parser.return_value
    config_handle.read.assert_called_once_with("consumer.ini")

    config_handle.__getitem__.assert_called_once_with(key_name)
    assert returned == config_handle.__getitem__.return_value


@patch("rabbit_consumer.rabbit_consumer.ConfigParser")
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
@patch("rabbit_consumer.rabbit_consumer.ConfigParser")
def test_load_config_throw_logs(config, exception):
    RabbitConsumer.reset()
    config.side_effect = exception()

    with pytest.raises(exception):
        RabbitConsumer.get_config()
