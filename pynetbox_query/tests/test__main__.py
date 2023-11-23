from unittest.mock import patch
from pytest import raises
from pynetboxquery.__main__ import main
from pynetboxquery.utils.error_classes import UserMethodNotFoundError


@patch("pynetboxquery.__main__.import_module")
@patch("pynetboxquery.__main__.getattr")
@patch("pynetboxquery.__main__.sys")
def test_main(mock_sys, mock_getattr, mock_import_module):
    mock_sys.argv.__getitem__.return_value = "upload_devices_to_netbox"
    mock_getattr.return_value.return_value = ["upload_devices_to_netbox"]
    main()
    mock_import_module.assert_called_with("pynetboxquery.user_methods.upload_devices_to_netbox")
    mock_getattr.assert_called_with(mock_import_module.return_value, "aliases")
    mock_import_module.return_value.main.assert_called_once_with()


@patch("pynetboxquery.__main__.import_module")
@patch("pynetboxquery.__main__.getattr")
@patch("pynetboxquery.__main__.sys")
def test_main_fail(mock_sys, mock_getattr, mock_import_module):
    mock_getattr.return_value.return_value = ["upload_devices_to_netbox"]
    with raises(UserMethodNotFoundError):
        main()


