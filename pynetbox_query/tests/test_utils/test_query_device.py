from unittest.mock import NonCallableMock, patch
from dataclasses import asdict
from pytest import fixture
from pynetboxquery.utils.query_device import QueryDevice


@fixture(name="instance")
def instance_fixture():
    """
    This fixture method returns the Class to be tested.
    """
    api = NonCallableMock()
    return QueryDevice(api)


def test_query_list_no_device(instance):
    """
    This test ensures that an empty list is returned if an empty list is given to the query list method.
    """
    mock_device_list = []
    with patch("pynetboxquery.utils.query_device.QueryDevice.query_device"):
        res = instance.query_list(mock_device_list)
    assert res == []


def test_query_list_one_device(instance):
    """
    This test ensures that one device is returned if one device is given to the method.
    """
    mock_device_list = [""]
    with patch(
        "pynetboxquery.utils.query_device.QueryDevice.query_device"
    ) as mock_query_device:
        res = instance.query_list(mock_device_list)
    assert res == [mock_query_device.return_value]


def test_query_list_multiple_devices(instance):
    """
    This test ensures 2 devices are returned if 2 devices are given.
    """
    mock_device_list = ["", ""]
    with patch(
        "pynetboxquery.utils.query_device.QueryDevice.query_device"
    ) as mock_query_device:
        res = instance.query_list(mock_device_list)
    assert res == [mock_query_device.return_value, mock_query_device.return_value]


def test_query_device(instance, mock_device, dict_to_device):
    """
    This test ensures the get_id is called on all fields in a dataclass.
    """
    with patch("pynetboxquery.utils.query_device.NetboxGetId.get_id") as mock_get_id:
        res = instance.query_device(mock_device)
    val = mock_get_id.return_value
    expected_device_dict = asdict(mock_device)
    for key in expected_device_dict.keys():
        expected_device_dict[key] = val
    assert res == dict_to_device(expected_device_dict)
