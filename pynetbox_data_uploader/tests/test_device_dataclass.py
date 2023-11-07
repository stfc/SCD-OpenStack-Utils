from lib.utils.device_dataclass import Device


def test_return_attrs():
    dev = Device(
        tenant="",
        device_role="",
        manufacturer="",
        device_type="",
        status="",
        site="",
        location="",
        rack="",
        face="",
        airflow="",
        position="",
        name="",
        serial="",
    )
    res = dev.return_attrs()
    expected = [
        'tenant',
        'device_role',
        'manufacturer',
        'device_type',
        'status',
        'site',
        'location',
        'rack',
        'face',
        'airflow',
        'position',
        'name',
        'serial',
    ]
    assert set(res) == set(expected)
