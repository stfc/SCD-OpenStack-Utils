from unittest.mock import MagicMock, NonCallableMock
from Netbox_Api.netbox_connect import NetboxConnect
import pytest


@pytest.fixture(name="instance")
def instance_fixture():
    url = NonCallableMock()
    token = NonCallableMock
    return NetboxConnect(url, token)


def test_api_object(instance):
    """
    This test checks that the Api method is called once.
    """
    mock_obj = MagicMock()
    instance.pnb = mock_obj
    instance.api_object()
    mock_obj.api.assert_called_once()
