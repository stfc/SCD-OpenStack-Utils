from unittest.mock import patch
from dataclasses import asdict
from pytest import fixture, raises
from user_methods.csv_to_netbox import (
    CsvToNetbox,
    arg_parser,
    do_csv_to_netbox,
    main,
)
from utils.error_classes import DeviceFoundError, DeviceTypeNotFoundError


@fixture(name="instance")
def instance_fixture():
    """
    This method calls the class being tested.
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


@patch("user_methods.csv_to_netbox.open_file")
@patch("user_methods.csv_to_netbox.separate_data")
def test_read_csv(mock_separate_data, mock_open_file, instance):
    """
    This test ensures the file open method is called and the separate data method is called.
    """
    mock_file_path = "mock_file_path"
    res = instance.read_csv(mock_file_path)
    mock_open_file.assert_called_once_with(mock_file_path)
    mock_separate_data.assert_called_once_with(mock_open_file.return_value)
    assert res == mock_separate_data.return_value


@patch("user_methods.csv_to_netbox.NetboxCheck.check_device_exists")
def test_check_netbox_device_does_exist(
    mock_check_device_exists, instance, mock_device
):
    """
    This test ensures that an error is raised if a device does exist in Netbox.
    """
    with raises(DeviceFoundError):
        instance.check_netbox_device([mock_device])
    mock_check_device_exists.assert_called_once_with(mock_device.name)


@patch("user_methods.csv_to_netbox.NetboxCheck.check_device_exists")
def test_check_netbox_device_not_exist(mock_check_device_exists, instance, mock_device):
    """
    This test ensures an error is not raised if a device does not exist in Netbox.
    """
    mock_check_device_exists.return_value = None
    instance.check_netbox_device([mock_device])
    mock_check_device_exists.assert_called_once_with(mock_device.name)


@patch("user_methods.csv_to_netbox.NetboxCheck.check_device_type_exists")
def test_check_netbox_device_type_does_exist(
    mock_check_device_type_exists, instance, mock_device
):
    """
    This test ensures an error is not raised if a device type does exist in Netbox.
    """
    instance.check_netbox_device_type([mock_device])
    mock_check_device_type_exists.assert_called_once_with(mock_device.device_type)


@patch("user_methods.csv_to_netbox.NetboxCheck.check_device_type_exists")
def test_check_netbox_device_type_not_exist(
    mock_check_device_type_exists, instance, mock_device
):
    """
    This test ensures an error is raised if a device type doesn't exist in Netbox.
    """
    mock_check_device_type_exists.return_value = None
    with raises(DeviceTypeNotFoundError):
        instance.check_netbox_device_type([mock_device])
    mock_check_device_type_exists.assert_called_once_with(mock_device.device_type)


@patch("user_methods.csv_to_netbox.QueryDevice.query_list")
def test_convert_data(mock_query_dataclass, instance):
    """
    This test ensures the convert data method is called with the correct arguments.
    """
    device_list = ["", ""]
    res = instance.convert_data(device_list)
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


@patch("user_methods.csv_to_netbox.NetboxCreate.create_device")
@patch("user_methods.csv_to_netbox.CsvToNetbox.dataclass_to_dict")
def test_send_data(mock_dataclass_to_dict, mock_create_device, instance):
    """
    This test ensures the correct methods are called with the correct arguments.
    """
    mock_device_list = ["", ""]
    res = instance.send_data(mock_device_list)
    mock_dataclass_to_dict.assert_called_once_with(mock_device_list)
    mock_create_device.assert_called_once_with(mock_dataclass_to_dict.return_value)
    assert res


@patch("user_methods.csv_to_netbox.argparse.ArgumentParser")
def test_arg_parser(mock_argparse):
    """
    This test ensures the argparse method adds the correct arguments and returns them.
    """
    res = arg_parser()
    mock_argparse.assert_called_once_with(
        description="Create devices in Netbox from CSV files.",
        usage="python csv_to_netbox.py url token file_path",
    )
    mock_argparse.return_value.add_argument.assert_any_call(
        "file_path", help="Your file path to csv files."
    )
    mock_argparse.return_value.add_argument.assert_any_call(
        "token", help="Your Netbox Token."
    )
    mock_argparse.return_value.add_argument.assert_any_call(
        "url", help="The Netbox URL."
    )
    mock_argparse.return_value.parse_args.assert_called()
    assert res == mock_argparse.return_value.parse_args()


@patch("user_methods.csv_to_netbox.CsvToNetbox")
def test_do_csv_to_netbox(mock_csv_to_netbox_class):
    """
    This test ensures all the correct methods are called with the correct arguments.
    """

    class Args:
        # pylint: disable=R0903
        """
        This class mocks the argument class in argparse.
        """

        def __init__(self, file_path, url, token):
            self.file_path = file_path
            self.url = url
            self.token = token

    args = Args("mock_file_path", "mock_url", "mock_token")
    res = do_csv_to_netbox(args)
    mock_csv_to_netbox_class.assert_any_call(url=args.url, token=args.token)
    mock_class_object = mock_csv_to_netbox_class.return_value
    mock_class_object.check_file_path.assert_any_call(args.file_path)
    mock_class_object.read_csv.assert_any_call(args.file_path)
    mock_device_list = mock_class_object.read_csv.return_value
    mock_class_object.check_netbox_device.assert_any_call(mock_device_list)
    mock_class_object.check_netbox_device_type.assert_any_call(mock_device_list)
    mock_class_object.convert_data.assert_any_call(mock_device_list)
    mock_converted_device_list = mock_class_object.convert_data.return_value
    mock_class_object.send_data.assert_any_call(mock_converted_device_list)
    assert res


@patch("user_methods.csv_to_netbox.arg_parser")
@patch("user_methods.csv_to_netbox.do_csv_to_netbox")
def test_main(mock_do_csv_to_netbox, mock_arg_parser):
    """
    This test ensures that when main is called the argparse method and do method are called with arguments.
    """
    main()
    mock_arg_parser.assert_called_once()
    mock_do_csv_to_netbox.assert_called_once_with(mock_arg_parser.return_value)
