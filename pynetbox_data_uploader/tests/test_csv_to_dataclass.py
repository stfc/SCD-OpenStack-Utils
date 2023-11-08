from csv import DictReader
from unittest.mock import patch, mock_open
from lib.utils.csv_to_dataclass import separate_data, open_file
from lib.utils.device_dataclass import Device


# Two tests mock the same Device dataclass and therefore have duplicate code.
# pylint: disable=R0801
def test_separate_data():
    """
    This test checks that when csv data is inputted the dataclass devices are created properly.
    """
    mock_data = [
        "tenant,device_role,manufacturer,device_type,status,"
        "site,location,rack,face,airflow,position,name,serial",
        "t1,dr1,m1,dt1,st1,si1,l1,r1,f1,a1,p1,n1,se1",
        "t2,dr2,m2,dt2,st2,si2,l2,r2,f2,a2,p2,n2,se2",
    ]
    mock_reader_obj = DictReader(mock_data)
    res = separate_data(mock_reader_obj)
    assert res[0] == Device(
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
    assert res[1] == Device(
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


def test_open_file():
    """
    This test ensures the csv file is opened appropriately and the DictReader method is called.
    """
    mock_data = (
        "tenant,device_role,manufacturer,device_type,status,site,location,rack,face,airflow,position,name,"
        "serial\nt1,dr1,m1,dt1,st1,si1,l1,r1,f1,a1,p1,n1,se1\nt2,dr2,m2,dt2,st2,si2,l2,r2,f2,a2,p2,n2,se2"
    )

    with patch("builtins.open", mock_open(read_data=mock_data)) as mock_file:
        res = open_file("mock_file_path")
    mock_file.assert_called_once_with("mock_file_path", encoding="UTF-8")
    expected = list(DictReader(mock_data.splitlines()))
    assert res == expected
