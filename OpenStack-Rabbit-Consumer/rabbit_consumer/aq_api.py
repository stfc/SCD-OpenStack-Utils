import logging
import subprocess
from typing import Optional, List

import requests
from requests.adapters import HTTPAdapter
from requests_kerberos import HTTPKerberosAuth
from urllib3.util.retry import Retry

from rabbit_consumer.consumer_config import ConsumerConfig
from rabbit_consumer.openstack_address import OpenstackAddress
from rabbit_consumer.os_descriptions.os_descriptions import OsDescription
from rabbit_consumer.rabbit_message import RabbitMessage
from rabbit_consumer.vm_data import VmData

MAKE_SUFFIX = "/host/{0}/command/make"

HOST_CHECK_SUFFIX = "/host/{0}"

UPDATE_INTERFACE_SUFFIX = "/machine/{0}/interface/{1}?boot&default_route"

DELETE_HOST_SUFFIX = "/host/{0}"
DELETE_MACHINE_SUFFIX = "/machine/{0}"

logger = logging.getLogger(__name__)


class AquilonError(Exception):
    """
    Base class for Aquilon errors
    """


def verify_kerberos_ticket():
    logger.debug("Checking for valid Kerberos Ticket")

    if subprocess.call(["klist", "-s"]) == 1:
        raise RuntimeError("No shared Kerberos ticket found.")

    logger.debug("Kerberos ticket success")
    return True


def setup_requests(url, method, desc, params: Optional[dict] = None):
    verify_kerberos_ticket()

    logger.debug("%s: %s", method, url)

    session = requests.Session()
    session.verify = "/etc/grid-security/certificates/aquilon-gridpp-rl-ac-uk-chain.pem"
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[503])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    if method == "post":
        response = session.post(url, auth=HTTPKerberosAuth(), params=params)
    elif method == "put":
        response = session.put(url, auth=HTTPKerberosAuth(), params=params)
    elif method == "delete":
        response = session.delete(url, auth=HTTPKerberosAuth(), params=params)
    else:
        response = session.get(url, auth=HTTPKerberosAuth(), params=params)

    if response.status_code == 400:
        # This might be an expected error, so don't log it
        logger.debug("AQ Error Response: %s", response.text)
        raise AquilonError(response.text)

    if response.status_code != 200:
        logger.error("%s: Failed: %s", desc, response.text)
        logger.error(url)
        raise ConnectionError(
            f"Failed {desc}: {response.status_code} -" "{response.text}"
        )

    logger.debug("Success: %s ", desc)
    logger.debug("Response: %s", response.text)
    return response.text


def aq_make(addresses: List[OpenstackAddress], os_data: OsDescription):
    params = {
        "personality": os_data.aq_default_personality,
        "osversion": os_data.aq_os_version,
        "osname": os_data.aq_os_name,
        "archetype": "cloud",
    }

    assert all(
        i for i in params.values()
    ), "Some fields were not set in the OS description"

    # Manage and make these back to default domain and personality
    for i in addresses:
        hostname = i.hostname
        logger.debug("Attempting to make templates for %s", hostname)

        if not hostname or not hostname.strip():
            raise ValueError("Hostname cannot be empty")

        url = ConsumerConfig().aq_url + MAKE_SUFFIX.format(hostname)
        setup_requests(url, "post", "Make Template: ", params)


def aq_manage(addresses: List[OpenstackAddress]):
    for i in addresses:
        hostname = i.hostname
        logger.debug("Attempting to manage %s", hostname)

        params = {
            "hostname": hostname,
            "domain": ConsumerConfig().aq_domain,
            "force": True,
        }
        url = ConsumerConfig().aq_url + f"/host/{hostname}/command/manage"
        setup_requests(url, "post", "Manage Host", params=params)


def create_machine(message: RabbitMessage, vm_data: VmData) -> str:
    logger.debug("Attempting to create machine for %s ", vm_data.virtual_machine_id)

    params = {
        "model": "vm-openstack",
        "serial": vm_data.virtual_machine_id,
        "vmhost": message.payload.vm_host,
        "cpucount": message.payload.vcpus,
        "memory": message.payload.memory_mb,
    }

    url = ConsumerConfig().aq_url + f"/next_machine/{ConsumerConfig().aq_prefix}"
    response = setup_requests(url, "put", "Create Machine", params=params)
    return response


def delete_machine(machinename):
    logger.debug("Attempting to delete machine for %s", machinename)

    url = ConsumerConfig().aq_url + DELETE_MACHINE_SUFFIX.format(machinename)

    setup_requests(url, "delete", "Delete Machine")


def create_host(
    os_details: OsDescription, addresses: List[OpenstackAddress], machine_name: str
):
    config = ConsumerConfig()

    for address in addresses:
        params = {
            "machine": machine_name,
            "ip": address.addr,
            "domain": config.aq_domain,
            "archetype": config.aq_archetype,
            "personality": config.aq_personality,
            "osname": os_details.aq_os_name,
            "osversion": os_details.aq_os_version,
        }

        logger.debug("Attempting to create host for %s ", address.hostname)
        url = config.aq_url + f"/host/{address.hostname}"
        setup_requests(url, "put", "Host Create", params=params)


def delete_host(hostname: str):
    logger.debug("Attempting to delete host for %s ", hostname)
    url = ConsumerConfig().aq_url + DELETE_HOST_SUFFIX.format(hostname)
    setup_requests(url, "delete", "Host Delete")


def add_machine_nics(machine_name, addresses: List[OpenstackAddress]):
    for i, address in enumerate(addresses):
        interface_name = f"eth{i}"

        logger.debug(
            "Attempting to add interface %s to machine %s ",
            interface_name,
            machine_name,
        )
        url = (
            ConsumerConfig().aq_url
            + f"/machine/{machine_name}/interface/{interface_name}"
        )
        setup_requests(
            url, "put", "Add Machine Interface", params={"mac": address.mac_addr}
        )

        params = {
            "machine": machine_name,
            "interface": interface_name,
            "ip": address.addr,
            "fqdn": address.hostname,
        }

        url = ConsumerConfig().aq_url + "/interface_address"
        setup_requests(url, "put", "Add Machine Interface Address", params=params)


def set_interface_bootable(machinename, interfacename):
    logger.debug("Attempting to bootable %s ", machinename)

    url = ConsumerConfig().aq_url + UPDATE_INTERFACE_SUFFIX.format(
        machinename, interfacename
    )

    setup_requests(url, "post", "Update Machine Interface")


def check_host_exists(hostname: str) -> bool:
    logger.debug("Checking if hostname exists: %s", hostname)
    url = ConsumerConfig().aq_url + HOST_CHECK_SUFFIX.format(hostname)
    try:
        setup_requests(url, "get", "Check Host")
    except AquilonError as err:
        if f"Host {hostname} not found." in str(err):
            return False
        raise
    return True
