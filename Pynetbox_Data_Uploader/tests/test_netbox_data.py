from unittest.mock import NonCallableMock
from netbox_api.netbox_data import NetboxGetID
import pytest


@pytest.fixture(name="instance")
def instance_fixture():
    netbox = NonCallableMock()
    return NetboxGetID(netbox)
