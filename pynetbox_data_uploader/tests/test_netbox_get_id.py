from unittest.mock import patch
from pytest import fixture
from lib.netbox_api.netbox_get_id import NetboxGetId


@fixture(name="instance")
def instance_fixture():
    """
    This function returns the class to be tested.
    """
    mock_api = ""
    return NetboxGetId(mock_api)


def test_get_id_tenant(instance, mock_device):
    """
    This test ensures the correct case is matched for the field.
    """
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "tenant")
        assert res == mock_netbox.tenancy.tenants.get().id


def test_get_id_device_role(instance, mock_device):
    """
    This test ensures the correct case is matched for the field.
    """
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "device_role")
        assert res == mock_netbox.dcim.device_roles.get().id


def test_get_id_manufacturer(instance, mock_device):
    """
    This test ensures the correct case is matched for the field.
    """
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "manufacturer")
        assert res == mock_netbox.dcim.manufacturers.get().id


def test_get_id_device_type(instance, mock_device):
    """
    This test ensures the correct case is matched for the field.
    """
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "device_type")
        assert res == mock_netbox.dcim.device_types.get().id


def test_get_id_site(instance, mock_device):
    """
    This test ensures the correct case is matched for the field.
    """
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "site")
        assert res == mock_netbox.dcim.sites.get().id


def test_get_id_location_site_str(instance, mock_device):
    """
    This test ensures the correct case is matched for the field.
    """
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "location")
        assert res == mock_netbox.dcim.locations.get().id


def test_get_id_location_site_int(instance, mock_device):
    """
    This test ensures the correct case is matched for the field.
    """
    mock_device.site = 1
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "location")
        assert res == mock_netbox.dcim.locations.get().id


def test_get_id_rack(instance, mock_device):
    """
    This test ensures the correct case is matched for the field.
    """
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "rack")
        assert res == mock_netbox.dcim.racks.get().id


def test_get_id_else(instance, mock_device):
    """
    This test ensures the correct case is matched for the field.
    """
    for field in ["status", "face", "airflow", "position", "name", "serial"]:
        res = instance.get_id(mock_device, field)
        assert res == getattr(mock_device, field)
