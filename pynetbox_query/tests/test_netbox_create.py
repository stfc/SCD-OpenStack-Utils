from unittest.mock import NonCallableMock
from dataclasses import asdict
from pytest import fixture
from pynetboxquery.netbox_api.netbox_create import NetboxCreate


@fixture(name="instance")
def instance_fixture():
    """
    This fixture method calls the class being tested.
    :return: The class object.
    """
    mock_api = NonCallableMock()
    return NetboxCreate(mock_api)


def test_create_device_one(instance, mock_device):
    """
    This test ensures the .create method is called once with the correct arguments.
    """
    mock_device_dict = asdict(mock_device)
    res = instance.create_device(mock_device_dict)
    instance.netbox.dcim.devices.create.assert_called_once_with(mock_device_dict)
    assert res


def test_create_device_many(instance, mock_device, mock_device_2):
    """
    This test ensures the .create method is called once with the correct arguments.
    """
    mock_device_dict = asdict(mock_device)
    mock_device_2_dict = asdict(mock_device_2)
    res = instance.create_device([mock_device_dict, mock_device_2_dict])
    instance.netbox.dcim.devices.create.assert_called_once_with(
        [mock_device_dict, mock_device_2_dict]
    )
    assert res


def test_create_device_type_one(instance):
    """
    This test ensures the .create method is called once with the correct arguments.
    """
    mock_device_type = ""
    res = instance.create_device_type(mock_device_type)
    instance.netbox.dcim.device_types.create.assert_called_once_with(mock_device_type)
    assert res


def test_create_device_type_many(instance):
    """
    This test ensures the .create method is called once with the correct arguments.
    """
    mock_device_type = ""
    mock_device_type_2 = ""
    res = instance.create_device_type([mock_device_type, mock_device_type_2])
    instance.netbox.dcim.device_types.create.assert_called_once_with(
        [mock_device_type, mock_device_type_2]
    )
    assert res
