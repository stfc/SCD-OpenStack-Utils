import logging
import subprocess

import requests
from requests.adapters import HTTPAdapter
from requests_kerberos import HTTPKerberosAuth
from urllib3.util.retry import Retry

from rabbit_consumer.rabbit_consumer import RabbitConsumer
from rabbit_consumer.consumer_config import ConsumerConfig

MODEL = "vm-openstack"
MAKE_SUFFIX = "/host/{0}/command/make"
MANAGE_SUFFIX = "/host/{0}/command/manage?hostname={0}&{1}={2}&force=true"
HOST_CHECK_SUFFIX = "/host/{0}"
CREATE_MACHINE_SUFFIX = (
    "/next_machine/{0}?model={1}&serial={2}&vmhost={3}&cpucount={4}&memory={5}"
)

ADD_INTERFACE_SUFFIX = "/machine/{0}/interface/{1}?mac={2}"

UPDATE_INTERFACE_SUFFIX = "/machine/{0}/interface/{1}?boot&default_route"

ADD_INTERFACE_ADDRESS_SUFFIX = (
    "/interface_address?machine={0}&interface={1}&ip={2}&fqdn={3}"
)
DEL_INTERFACE_ADDRESS_SUFFIX = "/interface_address?machine={0}&interface={1}&fqdn={2}"

DELETE_HOST_SUFFIX = "/host/{0}"
DELETE_MACHINE_SUFFIX = "/machine/{0}"

logger = logging.getLogger(__name__)


def verify_kerberos_ticket():
    logger.info("Checking for valid Kerberos Ticket")

    if subprocess.call(["klist", "-s"]) == 1:
        logger.warning("No ticket found / expired. Obtaining new one")
        kinit_cmd = ["kinit", "-k", f"HTTP/{ConsumerConfig().aq_fqdn}"]
        logger.debug("Running command: %s", kinit_cmd)

        subprocess.call(kinit_cmd)

        if subprocess.call(["klist", "-s"]) == 1:
            raise RuntimeError("Failed to obtain valid Kerberos ticket")

    logger.info("Kerberos ticket success")
    return True


def setup_requests(url, method, desc):
    verify_kerberos_ticket()

    logging.debug("%s: %s", method, url)

    session = requests.Session()
    session.verify = "/etc/grid-security/certificates/"
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[503])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    if method == "post":
        response = session.post(url, auth=HTTPKerberosAuth())
    elif method == "put":
        response = session.put(url, auth=HTTPKerberosAuth())
    elif method == "delete":
        response = session.delete(url, auth=HTTPKerberosAuth())
    else:
        response = session.get(url, auth=HTTPKerberosAuth())
    if response.status_code != 200:
        logger.error("%s: Failed: %s", desc, response.text)
        logger.error(url)
        raise ConnectionError(
            f"Failed {desc}: {response.status_code} -" "{response.text}"
        )

    logger.info("%s: Success ", desc)
    logger.debug("Response: %s", response.text)
    return response.text


def aq_make(hostname, personality=None, osversion=None, archetype=None, osname=None):
    logger.info("Attempting to make templates for %s", hostname)

    params = {
        "personality": personality,
        "osversion": osversion,
        "archetype": archetype,
        "osname": osname,
    }
    # Remove empty values or whitespace values
    params = {k: v for k, v in params.items() if v and str(v).strip()}
    if not hostname or not str(hostname).strip():
        raise ValueError("An empty hostname cannot be used.")

    # join remaining parameters to form url string
    params = [k + "=" + v for k, v in params.items()]

    url = (
        ConsumerConfig().aq_url + MAKE_SUFFIX.format(hostname) + "?" + "&".join(params)
    )
    if url[-1] == "?":
        # Trim trailing query param where there are no values
        url = url[:-1]

    setup_requests(url, "post", "Make Template: ")


def aq_manage(hostname, env_type, env_name):
    logger.info("Attempting to manage %s to %s %s", hostname, env_type, env_name)

    url = ConsumerConfig().aq_url + MANAGE_SUFFIX.format(hostname, env_type, env_name)

    setup_requests(url, "post", "Manage Host")


def create_machine(uuid, vmhost, vcpus, memory, hostname, prefix):
    logger.info("Attempting to create machine for %s ", hostname)

    url = ConsumerConfig().aq_url + CREATE_MACHINE_SUFFIX.format(
        prefix, MODEL, uuid, vmhost, vcpus, memory
    )

    response = setup_requests(url, "put", "Create Machine")
    return response


def delete_machine(machinename):
    logger.info("Attempting to delete machine for %s", machinename)

    url = ConsumerConfig().aq_url + DELETE_MACHINE_SUFFIX.format(machinename)

    setup_requests(url, "delete", "Delete Machine")


def create_host(
    hostname,
    machinename,
    firstip,
    osname,
    osversion,
):
    logger.info("Attempting to create host for %s ", hostname)
    config = ConsumerConfig()

    default_domain = config.aq_domain
    default_personality = config.aq_personality
    default_archetype = config.aq_archetype

    url = config.aq_url
    url += (
        f"/host/{hostname}?"
        f"machine={machinename}"
        f"&ip={firstip}"
        f"&archetype={default_archetype}"
        f"&domain={default_domain}"
        f"&personality={default_personality}"
        f"&osname={osname}"
        f"&osversion={osversion}"
    )

    logger.info(url)

    # reset personality etc ...
    setup_requests(url, "put", "Host Create")


def delete_host(hostname):
    logger.info("Attempting to delete host for %s ", hostname)

    url = ConsumerConfig().aq_url + DELETE_HOST_SUFFIX.format(hostname)

    setup_requests(url, "delete", "Host Delete")


def add_machine_interface(machinename, macaddr, interfacename):
    logger.info(
        "Attempting to add interface %s to machine %s ", interfacename, machinename
    )

    url = ConsumerConfig().aq_url + ADD_INTERFACE_SUFFIX.format(
        machinename, interfacename, macaddr
    )

    setup_requests(url, "put", "Add Machine Interface")


def add_machine_interface_address(machinename, ipaddr, interfacename, hostname):
    logger.info("Attempting to add address ip %s to machine %s ", ipaddr, machinename)

    url = ConsumerConfig().aq_url + ADD_INTERFACE_ADDRESS_SUFFIX.format(
        machinename, interfacename, ipaddr, hostname
    )

    setup_requests(url, "put", "Add Machine Interface Address")


def del_machine_interface_address(hostname, interfacename, machinename):
    logger.info("Attempting to delete address from machine %s ", machinename)

    url = ConsumerConfig().aq_url + DEL_INTERFACE_ADDRESS_SUFFIX.format(
        machinename, interfacename, hostname
    )

    setup_requests(url, "delete", "Del Machine Interface Address")


def update_machine_interface(machinename, interfacename):
    logger.info("Attempting to bootable %s ", machinename)

    url = ConsumerConfig().aq_url + UPDATE_INTERFACE_SUFFIX.format(
        machinename, interfacename
    )

    setup_requests(url, "post", "Update Machine Interface")


def set_env(
    hostname,
    domain=None,
    sandbox=None,
    personality=None,
    osversion=None,
    archetype=None,
    osname=None,
):
    if domain:
        aq_manage(hostname, "domain", domain)
    else:
        aq_manage(hostname, "sandbox", sandbox)

    aq_make(hostname, personality, osversion, archetype, osname)


def reset_env(hostname):
    # manage the host back to prod
    try:
        aq_manage(hostname, "domain", "prod_cloud")
    except Exception as err:
        raise Exception(f"Aquilon reset env failed: {err}") from err

    # reset personality etc ...
    try:
        # TODO this is SL6, are we using this?
        aq_make(hostname, "nubesvms", "6x-x86_64", "ral-tier1", "sl")
    except Exception as err:
        raise Exception(f"Aquilon reset personality: {err}") from err


def check_host_exists(hostname):
    logger.info("Attempting to make templates for %s", hostname)

    url = ConsumerConfig().aq_url + HOST_CHECK_SUFFIX.format(hostname)

    setup_requests(url, "get", "Check Host")
