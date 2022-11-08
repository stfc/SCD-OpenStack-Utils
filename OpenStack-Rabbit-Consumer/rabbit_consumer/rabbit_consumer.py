#!/usr/bin/python3
import enum
import logging
import sys
import time
from typing import Callable

from rabbit_consumer import message_consumer

logger = logging.getLogger(__name__)


class ConsumerState(enum.Enum):
    RUNNING = enum.auto()
    # Used to stop for testing only
    STOP = enum.auto()


class ConsumerLoop:
    state = ConsumerState.RUNNING

    def __init__(self, service: Callable):
        self._service = service

    def start(self):
        while self.state == ConsumerState.RUNNING:
            try:
                self._service()
            except Exception as e:
                logger.error(e)
                time.sleep(60)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.getLogger("pika").setLevel(logging.ERROR)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    consumer = ConsumerLoop(service=message_consumer.initiate_consumer)
    consumer.start()
