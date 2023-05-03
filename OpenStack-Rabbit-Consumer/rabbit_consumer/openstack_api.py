import logging
from typing import List

import openstack
from openstack.compute.v2.server import Server

from rabbit_consumer.consumer_config import ConsumerConfig
from rabbit_consumer.openstack_address import OpenstackAddress
from rabbit_consumer.vm_data import VmData

logger = logging.getLogger(__name__)


class OpenstackConnection:
    """
    Wrapper for Openstack connection, to reduce boilerplate code
    in subsequent functions.
    """

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.conn = None

    def __enter__(self):
        self.conn = openstack.connect(
            auth_url=ConsumerConfig().openstack_auth_url,
            project_name=self.project_name,
            username=ConsumerConfig().openstack_username,
            password=ConsumerConfig().openstack_password,
            user_domain_name=ConsumerConfig().openstack_domain_name,
            project_domain_name="default",
        )
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


def check_machine_exists(vm_data: VmData) -> bool:
    """
    Checks to see if the machine exists in Openstack.
    """
    with OpenstackConnection(vm_data.project_id) as conn:
        return bool(conn.compute.find_server(vm_data.virtual_machine_id))


def get_server_details(vm_data: VmData) -> Server:
    """
    Gets the server details from Openstack with details included
    """
    with OpenstackConnection(vm_data.project_id) as conn:
        # Workaround for details missing from find_server
        # on the current version of openstacksdk
        return list(conn.compute.servers(id=vm_data.virtual_machine_id, details=True))[
            0
        ]


def get_server_networks(vm_data: VmData) -> List[OpenstackAddress]:
    """
    Gets the networks from Openstack for the virtual machine as a list
    of deserialized OpenstackAddresses.
    """
    server = get_server_details(vm_data)
    return OpenstackAddress.get_internal_networks(server.addresses)


def get_metadata(vm_data: VmData) -> dict:
    """
    Gets the metadata from Openstack for the virtual machine.
    """
    server = get_server_details(vm_data)
    return server.metadata


def update_metadata(vm_data: VmData, metadata) -> None:
    """
    Updates the metadata for the virtual machine.
    """
    server = get_server_details(vm_data)
    with OpenstackConnection(vm_data.project_id) as conn:
        conn.compute.set_server_metadata(server, metadata)

    logger.debug("Setting metadata successful")
