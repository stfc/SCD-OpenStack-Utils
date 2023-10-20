import pytest
from unittest.mock import NonCallableMock
from lib.netbox_api.netbox_data import NetboxGetID


@pytest.fixture(name="instance")
def instance_fixture():
    """
    This fixture method calls the class being tested.
    :return: The class object.
    """
    netbox = NonCallableMock()
    return NetboxGetID(netbox)
