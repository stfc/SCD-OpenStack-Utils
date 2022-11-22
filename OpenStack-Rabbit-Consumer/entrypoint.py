#!/usr/bin/python3

import logging
import sys

from rabbit_consumer.rabbit_consumer import ConsumerLoop

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.getLogger("pika").setLevel(logging.ERROR)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    consumer = ConsumerLoop()
    consumer.start()
