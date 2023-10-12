from unittest.mock import MagicMock, NonCallableMock
from netbox_api.netbox_existence import NetboxExistence
import pytest


@pytest.fixture(name="api_mock", scope="function")
def instance_api_fixture():
    return MagicMock()


@pytest.fixture(name="instance")
def instance_fixture(api_mock):
    url = "not real url"
    token = "not real token"
    return NetboxExistence(url, token, api_mock)


def test_check_device_exists(instance):
    """
    This test ensures the .get method is called once with the correct argument.
    """
    mock_device = MagicMock()
    device_name = NonCallableMock()
    instance.netbox.dcim.devices = mock_device
    instance.check_device_exists(device_name)
    mock_device.get.assert_called_once_with(name=device_name)


def test_check_device_type_exists(instance):
    """
    This test ensures the .get method is called once with the correct argument.
    """
    mock_device_types = MagicMock()
    device_type = NonCallableMock()
    instance.netbox.dcim.device_types = mock_device_types
    instance.check_device_type_exists(device_type)
    mock_device_types.get.assert_called_once_with(slug=device_type)