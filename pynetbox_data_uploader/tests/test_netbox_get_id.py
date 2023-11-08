from pytest import fixture
from unittest.mock import patch
from lib.netbox_api.netbox_get_id import NetboxGetId
from lib.utils.device_dataclass import Device


@fixture(name="instance")
def instance_fixture():
    mock_api = ""
    return NetboxGetId(mock_api)


device_dict = {
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
        "serial": "se1"
    }
mock_device = Device(**device_dict)


def test_get_id_tenant(instance):
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "tenant")
        assert res == mock_netbox.tenancy.tenants.get().id


def test_get_id_device_role(instance):
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "device_role")
        assert res == mock_netbox.dcim.device_roles.get().id


def test_get_id_manufacturer(instance):
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "manufacturer")
        assert res == mock_netbox.dcim.manufacturers.get().id


def test_get_id_device_type(instance):
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "device_type")
        assert res == mock_netbox.dcim.device_types.get().id


def test_get_id_site(instance):
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "site")
        assert res == mock_netbox.dcim.sites.get().id


def test_get_id_location(instance):
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "location")
        assert res == mock_netbox.dcim.locations.get().id


def test_get_id_rack(instance):
    with patch.object(instance, "netbox") as mock_netbox:
        res = instance.get_id(mock_device, "rack")
        assert res == mock_netbox.dcim.racks.get().id


def test_get_id_else(instance):
    for field in ["status", "face", "airflow", "position", "name", "serial"]:
        res = instance.get_id(mock_device, field)
        assert res == getattr(mock_device, field)
