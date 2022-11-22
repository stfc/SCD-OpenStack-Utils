#!/usr/bin/python3

import logging
import signal
import sys

from rabbit_consumer.rabbit_consumer import ConsumerLoop


def _sigint_handler(*_):
    """
    Handles the SIGINT signal
    """
    logging.info("SIGINT received, shutting down")
    ConsumerLoop.state = ConsumerLoop.state.STOP


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.getLogger("pika").setLevel(logging.ERROR)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    signal.signal(signal.SIGINT, _sigint_handler)

    consumer = ConsumerLoop()
    consumer.start()
