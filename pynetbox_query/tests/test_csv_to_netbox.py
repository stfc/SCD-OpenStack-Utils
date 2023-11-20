from unittest.mock import patch
from pynetboxquery.user_methods import do_csv_to_netbox, main


@patch("user_methods.csv_to_netbox.TopLevelMethods")
def test_do_csv_to_netbox(mock_top_level_methods_class):
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
    mock_top_level_methods_class.assert_any_call(url="mock_url", token="mock_token")
    mock_class_object = mock_top_level_methods_class.return_value
    mock_class_object.check_file_path.assert_any_call("mock_file_path")
    mock_class_object.read_csv.assert_any_call("mock_file_path")
    mock_device_list = mock_class_object.read_csv.return_value
    mock_class_object.validate_devices.assert_any_call(mock_device_list)
    mock_class_object.validate_device_types.assert_any_call(mock_device_list)
    mock_class_object.query_data.assert_any_call(mock_device_list)
    mock_converted_device_list = mock_class_object.query_data.return_value
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
