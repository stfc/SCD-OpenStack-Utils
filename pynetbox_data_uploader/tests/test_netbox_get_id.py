from unittest.mock import NonCallableMock, patch
import pytest
from lib.netbox_api.netbox_get_id import NetboxGetID
from lib.enums.dcim_device_id import DeviceInfoID
from lib.enums.dcim_device_no_id import DeviceInfoNoID


@pytest.fixture(name="instance")
def instance_fixture():
    """
    This fixture method calls the class being tested.
    :return: The class object.
    """
    netbox = NonCallableMock()
    return NetboxGetID(netbox)


def test_get_id_from_key_with_id_enums(instance):
    """
    This test ensures that the get_id method is called for all properties in the DeviceInfoID enum.
    """
    with patch("lib.netbox_api.netbox_get_id.NetboxGetID.get_id") as mock_get_id:
        for member in [prop.name for prop in DeviceInfoID]:
            mock_dictionary = {member: "abc",
                               "site": "def"}
            res = instance.get_id_from_key(key=member, dictionary=mock_dictionary)
            mock_get_id.assert_called()
            assert res == mock_get_id.return_value


def test_get_id_from_key_with_no_id_enums(instance):
    """
    This test ensures that the get_id method is not called for all properties in the DeviceInfoNoID enum.
    """
    with patch("lib.netbox_api.netbox_get_id.NetboxGetID.get_id") as mock_get_id:
        for member in [prop.name for prop in DeviceInfoNoID]:
            mock_dictionary = {member: "abc",
                               "site": "def"}
            res = instance.get_id_from_key(key=member, dictionary=mock_dictionary)
            mock_get_id.assert_not_called()
            assert res == mock_dictionary[member]
