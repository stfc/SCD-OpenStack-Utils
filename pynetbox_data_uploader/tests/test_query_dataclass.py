from unittest.mock import NonCallableMock, patch
import pytest
from lib.utils.query_dataclass import QueryDataclass


@pytest.fixture(name="instance")
def instance_fixture():
    api = NonCallableMock()
    return QueryDataclass(api)


def test_query_list_no_device(instance):
    mock_device_list = []
    with patch("lib.utils.query_dataclass.QueryDataclass.query_device") as mock_query_device:
        res = instance.query_list(mock_device_list)
    assert res == []


def test_query_list_one_device(instance):
    mock_device_list = [""]
    with patch("lib.utils.query_dataclass.QueryDataclass.query_device") as mock_query_device:
        res = instance.query_list(mock_device_list)
    assert res == [mock_query_device.return_value]


def test_query_list_multiple_devices(instance):
    mock_device_list = ["", ""]
    with patch("lib.utils.query_dataclass.QueryDataclass.query_device") as mock_query_device:
        res = instance.query_list(mock_device_list)
    assert res == [mock_query_device.return_value, mock_query_device.return_value]

