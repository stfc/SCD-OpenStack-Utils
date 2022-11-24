#!/usr/bin/python3

import logging
import logging.handlers
import os
import signal
import sys
import queue


def _sigint_handler(*_):
    """
    Handles the SIGINT signal
    """
    # Note these imports need to happen in-line so
    # that the logging is configured before they are used
    from rabbit_consumer.rabbit_consumer import ConsumerLoop

    logging.info("SIGINT received, shutting down")
    ConsumerLoop.state = ConsumerLoop.state.STOP


def _prep_logging():
    logger = logging.getLogger("rabbit_consumer")
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    logger.addHandler(logging.StreamHandler(sys.stdout))

    logging.getLogger("pika").setLevel(logging.ERROR)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


if __name__ == "__main__":
    _prep_logging()

    signal.signal(signal.SIGINT, _sigint_handler)

    from rabbit_consumer.rabbit_consumer import ConsumerLoop

    consumer = ConsumerLoop()
    consumer.start()
