from unittest.mock import MagicMock
from Netbox_Api.netbox_connect import NetboxConnect
import pytest


@pytest.fixture(name="instance")
def instance_fixture():
    url = "not real url"
    token = "not real token"
    return NetboxConnect(url, token)


def test_api_object(instance):
    mock_obj = MagicMock()
    instance.pnb = mock_obj
    instance.api_object()
    mock_obj.api.assert_called_once()
