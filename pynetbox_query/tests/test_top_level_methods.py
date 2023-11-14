from unittest.mock import patch
from dataclasses import asdict
from pytest import fixture, raises
from pynetbox_query.top_level_methods import TopLevelMethods
from pynetbox_query.utils.error_classes import DeviceFoundError, DeviceTypeNotFoundError


@fixture(name="instance")
def instance_fixture():
    """
    This method calls the class being tested.
    """
    mock_url = "mock_url"
    mock_token = "mock_token"
    return TopLevelMethods(mock_url, mock_token)


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


@patch("pynetbox_query.top_level_methods.open_file")
@patch("pynetbox_query.top_level_methods.separate_data")
def test_read_csv(mock_separate_data, mock_open_file, instance):
    """
    This test ensures the file open method is called and the separate data method is called.
    """
    mock_file_path = "mock_file_path"
    res = instance.read_csv(mock_file_path)
    mock_open_file.assert_called_once_with(mock_file_path)
    mock_separate_data.assert_called_once_with(mock_open_file.return_value)
    assert res == mock_separate_data.return_value


@patch("pynetbox_query.top_level_methods.NetboxCheck.check_device_exists")
def test_validate_devices_do_exist(
    mock_check_device_exists, instance, mock_device
):
    """
    This test ensures that an error is raised if a device does exist in Netbox.
    """
    with raises(DeviceFoundError):
        instance.validate_devices([mock_device])
    mock_check_device_exists.assert_called_once_with(mock_device.name)


@patch("pynetbox_query.top_level_methods.NetboxCheck.check_device_exists")
def test_validate_devices_dont_exist(mock_check_device_exists, instance, mock_device):
    """
    This test ensures an error is not raised if a device does not exist in Netbox.
    """
    mock_check_device_exists.return_value = None
    instance.validate_devices([mock_device])
    mock_check_device_exists.assert_called_once_with(mock_device.name)


@patch("pynetbox_query.top_level_methods.NetboxCheck.check_device_type_exists")
def test_validate_device_types_do_exist(
    mock_check_device_type_exists, instance, mock_device
):
    """
    This test ensures an error is not raised if a device type does exist in Netbox.
    """
    instance.validate_device_types([mock_device])
    mock_check_device_type_exists.assert_called_once_with(mock_device.device_type)


@patch("pynetbox_query.top_level_methods.NetboxCheck.check_device_type_exists")
def test_validate_device_types_dont_exist(
    mock_check_device_type_exists, instance, mock_device
):
    """
    This test ensures an error is raised if a device type doesn't exist in Netbox.
    """
    mock_check_device_type_exists.return_value = None
    with raises(DeviceTypeNotFoundError):
        instance.validate_device_types([mock_device])
    mock_check_device_type_exists.assert_called_once_with(mock_device.device_type)


@patch("pynetbox_query.top_level_methods.QueryDevice.query_list")
def test_query_data(mock_query_dataclass, instance):
    """
    This test ensures the convert data method is called with the correct arguments.
    """
    device_list = ["", ""]
    res = instance.query_data(device_list)
    mock_query_dataclass.assert_any_call(device_list)
    assert res == mock_query_dataclass.return_value


def test_dataclass_to_dict(instance, mock_device, mock_device_2):
    """
    This test ensures that the Device dataclasses are returned as dictionaries when the method is called.
    """
    mock_device_list = [mock_device, mock_device_2]
    res = instance.dataclass_to_dict(mock_device_list)
    expected = [asdict(device) for device in mock_device_list]
    assert res == expected


@patch("pynetbox_query.top_level_methods.NetboxCreate.create_device")
@patch("pynetbox_query.top_level_methods.TopLevelMethods.dataclass_to_dict")
def test_send_data(mock_dataclass_to_dict, mock_create_device, instance):
    """
    This test ensures the correct methods are called with the correct arguments.
    """
    mock_device_list = ["", ""]
    res = instance.send_data(mock_device_list)
    mock_dataclass_to_dict.assert_called_once_with(mock_device_list)
    mock_create_device.assert_called_once_with(mock_dataclass_to_dict.return_value)
    assert res
