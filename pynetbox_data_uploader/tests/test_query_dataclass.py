from unittest.mock import NonCallableMock, patch
import pytest
from lib.utils.query_device import QueryDevice
from lib.utils.device_dataclass import Device


@pytest.fixture(name="instance")
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
    with patch("lib.utils.query_device.QueryDevice.query_device"):
        res = instance.query_list(mock_device_list)
    assert res == []


def test_query_list_one_device(instance):
    """
    This test ensures that one device is returned if one device is given to the method.
    """
    mock_device_list = [""]
    with patch("lib.utils.query_device.QueryDevice.query_device") as mock_query_device:
        res = instance.query_list(mock_device_list)
    assert res == [mock_query_device.return_value]


def test_query_list_multiple_devices(instance):
    """
    This test ensures 2 devices are returned if 2 devices are given.
    """
    mock_device_list = ["", ""]
    with patch("lib.utils.query_device.QueryDevice.query_device") as mock_query_device:
        res = instance.query_list(mock_device_list)
    assert res == [mock_query_device.return_value, mock_query_device.return_value]


def test_query_device(instance):
    """
    This test ensures the get_id is called on all fields in a dataclass.
    """
    device_dict = {
        "tenant": "t2",
        "device_role": "dr2",
        "manufacturer": "m2",
        "device_type": "dt2",
        "status": "st2",
        "site": "si2",
        "location": "l2",
        "rack": "r2",
        "face": "f2",
        "airflow": "a2",
        "position": "p2",
        "name": "n2",
        "serial": "se2",
    }
    with patch("lib.utils.query_device.NetboxGetId.get_id") as mock_get_id:
        res = instance.query_device(Device(**device_dict))
    val = mock_get_id.return_value
    expected_device_dict = {
        "tenant": val,
        "device_role": val,
        "manufacturer": val,
        "device_type": val,
        "status": val,
        "site": val,
        "location": val,
        "rack": val,
        "face": val,
        "airflow": val,
        "position": val,
        "name": val,
        "serial": val,
    }
    assert res == Device(**expected_device_dict)
