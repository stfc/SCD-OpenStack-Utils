#!/usr/bin/python
import sys
import logging
import time

import common
import message_consumer

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.getLogger("pika").setLevel(logging.ERROR)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    common.load_config()

    while True:
        try:
            message_consumer.initiate_consumer()
        except Exception as e:
            logger.error(e)
            time.sleep(60)
