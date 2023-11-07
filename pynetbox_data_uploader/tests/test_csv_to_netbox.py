from unittest.mock import patch
from pytest import fixture, raises
from lib.user_methods.csv_to_netbox import CsvToNetbox
from lib.utils.device_dataclass import Device


@fixture(name="instance")
def instance_fixture():
    """
    This method calls the class being tested.
    :return: The class with mock arguments.
    """
    mock_url = "mock_url"
    mock_token = "mock_token"
    return CsvToNetbox(mock_url, mock_token)


def test_check_file_path_valid(instance):
    """
    This test checks that the method doesn't raise any errors for valid filepaths.
    """
    mock_file_path = "."
    instance.check_file_path(mock_file_path)


def test_check_file_path_invalid(instance):
    """
    This test checks that the method raises an error when the filepath is invalid.
    """
    mock_file_path = ">"
    with raises(FileNotFoundError):
        instance.check_file_path(mock_file_path)


@patch("lib.user_methods.csv_to_netbox.open_file")
@patch("lib.user_methods.csv_to_netbox.separate_data")
def test_read_csv(mock_separate_data, mock_open_file, instance):
    mock_file_path = "mock_file_path"
    res = instance.read_csv(mock_file_path)
    mock_open_file.assert_called_once_with(mock_file_path)
    mock_separate_data.assert_called_once_with(mock_open_file.return_value)
    assert res == mock_separate_data.return_value


@patch("lib.user_methods.csv_to_netbox.NetboxCheck.check_device_exists")
def test_check_netbox_device_does_exist(mock_check_device_exists, instance):
    device = Device(
        tenant="t1",
        device_role="dr1",
        manufacturer="m1",
        device_type="dt1",
        status="st1",
        site="si1",
        location="l1",
        rack="r1",
        face="f1",
        airflow="a1",
        position="p1",
        name="n1",
        serial="se1",
    )
    with raises(Exception):
        instance.check_netbox_device([device])


@patch("lib.user_methods.csv_to_netbox.NetboxCheck.check_device_exists")
def test_check_netbox_device_not_exist(mock_check_device_exists, instance):
    device = Device(
        tenant="t1",
        device_role="dr1",
        manufacturer="m1",
        device_type="dt1",
        status="st1",
        site="si1",
        location="l1",
        rack="r1",
        face="f1",
        airflow="a1",
        position="p1",
        name="n1",
        serial="se1",
    )
    mock_check_device_exists.return_value = None
    instance.check_netbox_device([device])


@patch("lib.user_methods.csv_to_netbox.NetboxCheck.check_device_type_exists")
def test_check_netbox_device_type_does_exist(mock_check_device_type_exists, instance):
    device = Device(
        tenant="t1",
        device_role="dr1",
        manufacturer="m1",
        device_type="dt1",
        status="st1",
        site="si1",
        location="l1",
        rack="r1",
        face="f1",
        airflow="a1",
        position="p1",
        name="n1",
        serial="se1",
    )
    instance.check_netbox_device_type([device])


@patch("lib.user_methods.csv_to_netbox.NetboxCheck.check_device_type_exists")
def test_check_netbox_device_type_not_exist(mock_check_device_type_exists, instance):
    device = Device(
        tenant="t1",
        device_role="dr1",
        manufacturer="m1",
        device_type="dt1",
        status="st1",
        site="si1",
        location="l1",
        rack="r1",
        face="f1",
        airflow="a1",
        position="p1",
        name="n1",
        serial="se1",
    )
    mock_check_device_type_exists.return_value = None
    with raises(Exception):
        instance.check_netbox_device_type([device])

    