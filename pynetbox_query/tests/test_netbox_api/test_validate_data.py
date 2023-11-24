from unittest.mock import patch, NonCallableMock
from pytest import fixture
from pynetboxquery.netbox_api.validate_data import ValidateData


@fixture(name="instance")
def instance_fixture():
    """
    This fixture returns the class instance to be tested.
    """
    return ValidateData()


@patch("pynetboxquery.netbox_api.validate_data.ValidateData._call_validation_methods")
def test_validate_data_one_field(
    mock_call_validation_methods, instance, mock_device_list
):
    """
    This test ensures that the correct methods are called when validating one field.
    """
    mock_netbox_api = ""
    mock_fields = ["field1"]
    instance.validate_data(mock_device_list, mock_netbox_api, mock_fields)
    mock_call_validation_methods.assert_called_once_with(
        mock_device_list, mock_netbox_api, mock_fields[0]
    )


@patch("pynetboxquery.netbox_api.validate_data.ValidateData._call_validation_methods")
def test_validate_data_many_fields(
    mock_call_validation_methods, instance, mock_device_list
):
    """
    This test ensures that the correct methods are called when validating more than one field.
    """
    mock_netbox_api = ""
    mock_fields = ["field1", "field2"]
    instance.validate_data(mock_device_list, mock_netbox_api, mock_fields)
    mock_call_validation_methods.assert_any_call(
        mock_device_list, mock_netbox_api, mock_fields[0]
    )
    mock_call_validation_methods.assert_any_call(
        mock_device_list, mock_netbox_api, mock_fields[1]
    )


@patch("pynetboxquery.netbox_api.validate_data.ValidateData._call_validation_methods")
@patch("pynetboxquery.netbox_api.validate_data.print")
def test_validate_data_one_result(
    mock_print, mock_call_validation_methods, instance, mock_device_list
):
    """
    This test ensures that the correct methods are called when printing one set of results.
    """
    mock_netbox_api = ""
    mock_fields = ["field1"]
    mock_call_validation_methods.return_value = ["result1"]
    instance.validate_data(mock_device_list, mock_netbox_api, mock_fields)
    assert mock_print.call_count == 1


@patch("pynetboxquery.netbox_api.validate_data.ValidateData._call_validation_methods")
@patch("pynetboxquery.netbox_api.validate_data.print")
def test_validate_data_many_results(
    mock_print, mock_call_validation_methods, instance, mock_device_list
):
    """
    This test ensures that the correct methods are called when printing more than one set of results.
    """
    mock_netbox_api = ""
    mock_fields = ["field1"]
    mock_call_validation_methods.return_value = ["result1", "result2"]
    instance.validate_data(mock_device_list, mock_netbox_api, mock_fields)
    assert mock_print.call_count == 2


@patch(
    "pynetboxquery.netbox_api.validate_data.ValidateData._check_list_device_name_in_netbox"
)
def test_call_validation_methods_name(
    mock_check_list_device_name_in_netbox, instance, mock_device_list
):
    """
    This test ensures the correct methods are called when validating the name field.
    """
    mock_netbox_api = ""
    res = instance._call_validation_methods(mock_device_list, mock_netbox_api, "name")
    mock_device_values = [device.name for device in mock_device_list]
    mock_check_list_device_name_in_netbox.assert_called_once_with(
        mock_device_values, mock_netbox_api
    )
    assert res == mock_check_list_device_name_in_netbox.return_value


@patch(
    "pynetboxquery.netbox_api.validate_data.ValidateData._check_list_device_type_in_netbox"
)
def test_call_validation_methods_type(
    mock_check_list_device_type_in_netbox, instance, mock_device_list
):
    """
    This test ensures the correct methods are called when validating the device_type field.
    """
    mock_netbox_api = ""
    res = instance._call_validation_methods(
        mock_device_list, mock_netbox_api, "device_type"
    )
    mock_device_values = [device.device_type for device in mock_device_list]
    mock_check_list_device_type_in_netbox.assert_called_once_with(
        mock_device_values, mock_netbox_api
    )
    assert res == mock_check_list_device_type_in_netbox.return_value


def test_call_validation_methods_wildcard(instance, mock_device_list):
    """
    This test ensures the correct methods are called when validating a field that doesn't exist.
    """
    mock_netbox_api = ""
    res = instance._call_validation_methods(
        mock_device_list, mock_netbox_api, "wildcard"
    )
    assert res == ["Could not find a field for the argument: wildcard."]


def test_check_device_name_in_netbox(instance):
    """
    This test ensures the .get() method is called with the correct arguments when checking the device name.
    """
    netbox_api = NonCallableMock()
    res = instance._check_device_name_in_netbox("name", netbox_api)
    netbox_api.dcim.devices.get.assert_called_once_with(name="name")
    assert res


@patch(
    "pynetboxquery.netbox_api.validate_data.ValidateData._check_device_name_in_netbox"
)
def test_check_list_device_name_in_netbox_one(
    mock_check_device_name_in_netbox, instance
):
    """
    This test ensures the correct methods are called for checking a list of device names that holds one value.
    """
    res = instance._check_list_device_name_in_netbox(["name"], "api")
    mock_check_device_name_in_netbox.assert_called_once_with("name", "api")
    assert res == [
        f"Device name exists in Netbox: {mock_check_device_name_in_netbox.return_value}."
    ]


@patch(
    "pynetboxquery.netbox_api.validate_data.ValidateData._check_device_name_in_netbox"
)
def test_check_list_device_name_in_netbox_many(
    mock_check_device_name_in_netbox, instance
):
    """
    This test ensures the correct methods are called for checking a list of device names that holds many values.
    """
    res = instance._check_list_device_name_in_netbox(["name1", "name2"], "api")
    mock_check_device_name_in_netbox.assert_any_call("name1", "api")
    mock_check_device_name_in_netbox.assert_any_call("name2", "api")
    assert res == [
        f"Device name1 exists in Netbox: {mock_check_device_name_in_netbox.return_value}.",
        f"Device name2 exists in Netbox: {mock_check_device_name_in_netbox.return_value}.",
    ]


def test_check_device_type_in_netbox(instance):
    """
    This test ensures the .get() method is called with the correct arguments when checking the device type.
    """
    netbox_api = NonCallableMock()
    res = instance._check_device_type_in_netbox("type", netbox_api)
    netbox_api.dcim.device_types.get.assert_called_once_with(slug="type")
    assert res


@patch(
    "pynetboxquery.netbox_api.validate_data.ValidateData._check_device_type_in_netbox"
)
def test_check_list_device_type_in_netbox_one(
    mock_check_device_type_in_netbox, instance
):
    """
    This test ensures the correct methods are called for checking a list of device types that holds one value.
    """
    res = instance._check_list_device_type_in_netbox(["type"], "api")
    mock_check_device_type_in_netbox.assert_called_once_with("type", "api")
    assert res == [
        f"Device type type exists in Netbox: {mock_check_device_type_in_netbox.return_value}."
    ]


@patch(
    "pynetboxquery.netbox_api.validate_data.ValidateData._check_device_type_in_netbox"
)
def test_check_list_device_type_in_netbox_many(
    mock_check_device_type_in_netbox, instance
):
    """
    This test ensures the correct methods are called for checking a list of device types that holds many values.
    """
    res = instance._check_list_device_type_in_netbox(["type1", "type2"], "api")
    mock_check_device_type_in_netbox.assert_any_call("type1", "api")
    mock_check_device_type_in_netbox.assert_any_call("type2", "api")
    assert res == [
        f"Device type type1 exists in Netbox: {mock_check_device_type_in_netbox.return_value}.",
        f"Device type type2 exists in Netbox: {mock_check_device_type_in_netbox.return_value}.",
    ]
