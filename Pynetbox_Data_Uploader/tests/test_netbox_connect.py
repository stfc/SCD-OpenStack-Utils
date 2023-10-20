import pytest
from unittest.mock import NonCallableMock, patch
from lib.netbox_api.netbox_connect import NetboxConnect


@pytest.fixture(name="instance")
def instance_fixture():
    url = NonCallableMock()
    token = NonCallableMock()
    return NetboxConnect(url, token)


def test_api_object(instance):
    """
    This test checks that the Api method is called once.
    """
    with patch("lib.netbox_api.netbox_connect.nb") as mock_netbox:
        res = instance.api_object()
    mock_netbox.api.assert_called_once_with(instance.url, instance.token)
    assert res == mock_netbox.api.return_value
