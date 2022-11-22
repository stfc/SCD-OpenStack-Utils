import enum
import logging
from typing import Callable

from rabbit_consumer import message_consumer

logger = logging.getLogger(__name__)


class ConsumerState(enum.Enum):
    """
    Holds the state of the consumer loop, this is primarily
    used in unit tests to stop the loop
    """

    RUNNING = enum.auto()
    STOP = enum.auto()


# pylint: disable=too-few-public-methods
class ConsumerLoop:
    """
    Runs the main consumer loop continuously,
    this is the main entrypoint for the application.
    """

    state = ConsumerState.RUNNING

    def __init__(self, service: Callable = message_consumer.initiate_consumer):
        self._service = service

    def start(self):
        while self.state == ConsumerState.RUNNING:
            try:
                self._service()
            # pylint: disable=broad-except
            except Exception as err:
                logger.error(err)
                time.sleep(60)
