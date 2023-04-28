import uuid

import pytest

from rabbit_consumer.openstack_address import OpenstackAddress
from rabbit_consumer.rabbit_message import RabbitMessage, RabbitMeta, RabbitPayload
from rabbit_consumer.vm_data import VmData


@pytest.fixture(name="rabbit_message")
def fixture_rabbit_message():
    rabbit_payload = RabbitPayload(
        fixed_ips=["127.0.0.1"],
        image_name="image_name_mock",
        instance_id="instance_id_mock",
        memory_mb=1024,
        metadata=RabbitMeta(),
        user_name="user_name_mock",
        vcpus=2,
        vm_host="vm_host_mock",
        vm_name="vm_name_mock",
    )

    return RabbitMessage(
        event_type="event_type_mock",
        payload=rabbit_payload,
        project_id="project_id_mock",
        project_name="project_name_mock",
        user_name="user_name_mock",
    )


@pytest.fixture(name="vm_data")
def fixture_vm_data():
    return VmData(
        project_id="project_id_mock", virtual_machine_id="virtual_machine_id_mock"
    )


@pytest.fixture(name="openstack_address")
def fixture_openstack_address():
    return OpenstackAddress(
        addr="127.0.0.123",
        mac_addr="00:00:00:00:00:00",
        version=4,
        hostname=str(uuid.uuid4()),
    )


@pytest.fixture(name="openstack_address_list")
def fixture_openstack_address_list(openstack_address):
    addresses = [openstack_address, openstack_address]
    for i in addresses:
        # Set a unique hostname for each address, otherwise the fixture
        # will return the same object twice
        i.hostname = str(uuid.uuid4())
    return addresses
