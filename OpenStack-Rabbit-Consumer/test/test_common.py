from unittest.mock import patch

import rabbit_consumer
from rabbit_consumer.common import load_config


@patch("rabbit_consumer.common.SafeConfigParser")
def test_load_config(config_parser):
    # TODO drop global for singleton
    assert rabbit_consumer.common.config is None

    load_config()
    config_handle = config_parser.return_value
    assert rabbit_consumer.common.config == config_handle

    config_handle.read.assert_called_once_with("/etc/openstack-utils/consumer.ini")


@patch("rabbit_consumer.common.SafeConfigParser")
@patch("rabbit_consumer.common.logger")
@patch("rabbit_consumer.common.sys.exit")
def test_load_config_throw_logs(_, logger, config):
    # TODO check this just escalates the warning
    config.side_effect = IOError()

    load_config()
    logger.error.assert_called_once()
