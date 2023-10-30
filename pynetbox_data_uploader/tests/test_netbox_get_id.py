from unittest.mock import NonCallableMock
import pytest
from lib.netbox_api.netbox_get_id import NetboxGetID


@pytest.fixture(name="instance")
def instance_fixture():
    """
    This fixture method calls the class being tested.
    :return: The class object.
    """
    netbox = NonCallableMock()
    return NetboxGetID(netbox)
