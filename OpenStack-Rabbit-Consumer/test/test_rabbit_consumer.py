from typing import Tuple
from unittest.mock import Mock

from rabbit_consumer.rabbit_consumer import ConsumerLoop, ConsumerState


def _get_prepared_loop() -> Tuple[ConsumerLoop, Mock]:
    def _stop_while_loop(instance: ConsumerLoop):
        instance.state = ConsumerState.STOP

    service = Mock()
    app = ConsumerLoop(service)

    service.side_effect = lambda: _stop_while_loop(app)
    return app, service


def test_consumer_loop_initiates_consumption():
    app, service = _get_prepared_loop()
    app.start()
    service.assert_called_once()
