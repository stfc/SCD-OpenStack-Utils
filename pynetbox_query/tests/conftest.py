from typing import Dict
from pytest import fixture
from pynetboxquery.utils.device_dataclass import Device


@fixture(scope="function", name="dict_to_device")
def dict_to_device_instance():
    """
    This fixture returns a helper function to create Device Dataclasses from dictionaries.
    """

    def func(dictionary: Dict) -> Device:
        return Device(**dictionary)

    return func


@fixture(scope="function", name="mock_device")
def mock_device_fixture(dict_to_device):
    """
    This method returns a device dataclass.
    """
    device = {
        "tenant": "t1",
        "device_role": "dr1",
        "manufacturer": "m1",
        "device_type": "dt1",
        "status": "st1",
        "site": "si1",
        "location": "l1",
        "rack": "r1",
        "face": "f1",
        "airflow": "a1",
        "position": "p1",
        "name": "n1",
        "serial": "se1",
    }
    return dict_to_device(device)


@fixture(scope="function", name="mock_device_2")
def mock_device_2_fixture(dict_to_device):
    """
    This method returns a second device dataclass.
    """
    device = {
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
    return dict_to_device(device)


@fixture(scope="function", name="mock_device_list")
def mock_device_list_fixture(mock_device, mock_device_2):
    """
    This fixture returns a list of mock device types.
    """
    return [mock_device, mock_device_2]
