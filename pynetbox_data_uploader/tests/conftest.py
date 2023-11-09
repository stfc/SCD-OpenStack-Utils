from pytest import fixture
from lib.utils.device_dataclass import Device


@fixture(scope="function", name="mock_device")
def mock_device_fixture():
    """
    This method returns a device dataclass.
    """
    return Device(
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


@fixture(scope="function", name="mock_device_2")
def mock_device_2_fixture():
    """
    This method returns a second device dataclass.
    """
    return Device(
        tenant="t2",
        device_role="dr2",
        manufacturer="m2",
        device_type="dt2",
        status="st2",
        site="si2",
        location="l2",
        rack="r2",
        face="f2",
        airflow="a2",
        position="p2",
        name="n2",
        serial="se2",
    )
