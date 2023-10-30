from unittest.mock import MagicMock, NonCallableMock
import pytest
from lib.netbox_api.netbox_create import NetboxCreate


@pytest.fixture(name="instance")
def instance_fixture():
    """
    This fixture method calls the class being tested.
    :return: The class object.
    """
    netbox = NonCallableMock()
    return NetboxCreate(netbox)


def test_create_device(instance):
    """
    This test ensures the .create method is called once with the correct argument.
    """
    mock_device = MagicMock()
    mock_data = NonCallableMock()
    instance.netbox.dcim.devices = mock_device
    instance.create_device(mock_data)
    mock_device.create.assert_called_once_with(mock_data)


def test_create_device_type(instance):
    """
    This test ensures the .creat method is called once with the correct arguments.
    """
    mock_device_types = MagicMock()
    mock_model = NonCallableMock()
    mock_slug = NonCallableMock()
    mock_manufacturer = NonCallableMock()
    instance.netbox.dcim.device_types = mock_device_types
    instance.create_device_type(
        model=mock_model, manufacturer=mock_manufacturer, slug=mock_slug
    )
    mock_device_types.create.assert_called_once_with(
        model=mock_model, slug=mock_slug, manufacturer=mock_manufacturer, u_height=0
    )
