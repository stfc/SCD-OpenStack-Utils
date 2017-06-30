import logging

from ConfigParser import SafeConfigParser

logger = logging.getLogger(__name__)

config = None

def load_config():
    global config
    try:
        config = SafeConfigParser()
        config.read("/etc/openstack-utils/consumer.ini")
    except Exception as e:
        logger.error("Failed to load the config file " + str(e))
        sys.exit(1)