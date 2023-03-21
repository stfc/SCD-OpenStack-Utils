import json
import logging
import socket

import rabbitpy

from rabbit_consumer import aq_api
from rabbit_consumer import openstack_api
from rabbit_consumer.aq_api import verify_kerberos_ticket
from rabbit_consumer.consumer_config import ConsumerConfig
from rabbit_consumer.aq_fields import AqFields

logger = logging.getLogger(__name__)


def is_aq_message(message):
    """
    Check to see if the metadata in the message contains entries that suggest it
    is for an Aquilon VM.
    """
    metadata = message.get("payload").get("metadata")
    if metadata:
        if set(metadata.keys()).intersection(
            [
                "AQ_DOMAIN",
                "AQ_SANDBOX",
                "AQ_OSVERSION",
                "AQ_PERSONALITY",
                "AQ_ARCHETYPE",
                "AQ_OS",
            ]
        ):
            return True
    if metadata:
        if set(metadata.keys()).intersection(
            [
                "aq_domain",
                "aq_sandbox",
                "aq_osversion",
                "aq_personality",
                "aq_archetype",
                "aq_os",
            ]
        ):
            return True
    metadata = message.get("payload").get("image_meta")

    if metadata:
        if set(metadata.keys()).intersection(
            [
                "AQ_DOMAIN",
                "AQ_SANDBOX",
                "AQ_OSVERSION",
                "AQ_PERSONALITY",
                "AQ_ARCHETYPE",
                "AQ_OS",
            ]
        ):
            return True
    if metadata:
        if set(metadata.keys()).intersection(
            [
                "aq_domain",
                "aq_sandbox",
                "aq_osversion",
                "aq_personality",
                "aq_archetype",
                "aq_os",
            ]
        ):
            return True

    return False


def get_metadata_value(message, key):
    """
    Function which gets the value from the possible for a given metadata key
    from the possible paths in the image or instance metadata with
    the key in uppercase or lowercase
    """
    returnstring = message.get("payload").get("metadata").get(key)
    if returnstring is None:
        returnstring = message.get("payload").get("image_meta").get(key)
        if returnstring is None:
            returnstring = message.get("payload").get("metadata").get(key.lower())
            if returnstring is None:
                returnstring = message.get("payload").get("image_meta").get(key.lower())
    return returnstring


def consume(message):
    event = message.get("event_type")
    if event == "compute.instance.create.end":
        _handle_create_machine(message)

    if event == "compute.instance.delete.start":
        _handle_machine_delete(message)


def _handle_machine_delete(message):
    if is_aq_message(message):
        logger.debug("Message: %s", message)
        logger.info("=== Received Aquilon VM delete message ===")

        project_name = message.get("_context_project_name")
        project_id = message.get("_context_project_id")
        vm_id = message.get("payload").get("instance_id")
        vm_name = message.get("payload").get("display_name")
        username = message.get("_context_user_name")
        metadata = message.get("payload").get("metadata")
        machinename = message.get("payload").get("metadata").get("AQ_MACHINENAME")
        hostnames = metadata.get("HOSTNAMES", None)

        if not hostnames:
            logger.debug("No hostnames found in metadata, skipping delete")
            return

        hostnames = [
            i
            for i in hostnames.split(",")
            if "novalocal".casefold() not in i.casefold()
        ]
        if not hostnames:
            logger.info("Skipping unregistered host (metadata): %s", metadata)
            return

        logger.debug("Project Name: %s (%s)", project_name, project_id)
        logger.debug("VM Name: %s (%s) ", vm_name, vm_id)
        logger.debug("Username: %s", username)
        logger.debug("Hostnames: %s", hostnames)

        try:
            for host in metadata.get("HOSTNAMES").split(","):
                logger.debug("Host cleanup: %s", host)
                aq_api.delete_host(host)

            logger.debug("Deleting machine: %s", machinename)
            aq_api.delete_machine(machinename)
        except ConnectionError:
            openstack_api.update_metadata(project_id, vm_id, {"AQ_STATUS": "FAILED"})

        logger.info("=== Finished Aquilon deletion hook for VM %s ===", vm_name)


def _handle_create_machine(message):
    if is_aq_message(message):
        logger.info("=== Received Aquilon VM create message ===")

        project_name = message.get("_context_project_name")
        vm_id = message.get("payload").get("instance_id")
        vm_name = message.get("payload").get("display_name")
        username = message.get("_context_user_name")

        aq_details = AqFields(
            archetype=get_metadata_value(message, "AQ_ARCHETYPE"),
            hostnames=convert_hostnames(message),
            osname=get_metadata_value(message, "AQ_OS"),
            osversion=get_metadata_value(message, "AQ_OSVERSION"),
            personality=get_metadata_value(message, "AQ_PERSONALITY"),
            project_id=message.get("_context_project_id"),
        )

        if not aq_details.hostnames:
            logger.info("Skipping novalocal only host: %s", vm_name)
            return

        logger.debug("Project Name: %s (%s)", project_name, aq_details.project_id)
        logger.debug("VM Name: %s (%s) ", vm_name, vm_id)
        logger.debug("Username: %s", username)
        logger.debug("Hostnames: %s", aq_details.hostnames)

        _add_hostname_to_metadata(aq_details, vm_id)
        firstip, machinename = _aq_create_machine(aq_details.hostnames, message)
        _aq_add_first_nic(machinename, message)
        _aq_add_optional_nics(aq_details.hostnames, machinename, message)
        _aq_update_machine_nic(machinename)
        _aq_create_host(firstip, machinename, vm_id, aq_details)

        # as the machine may have been assigned more that one ip address,
        # apply the aquilon configuration to all of them
        _aq_make_machines(aq_details, vm_id)

        logger.debug("Successfully applied Aquilon configuration")
        openstack_api.update_metadata(
            aq_details.project_id, vm_id, {"AQ_STATUS": "SUCCESS"}
        )

        logger.info("=== Finished Aquilon creation hook for VM %s ===", vm_name)


def _aq_make_machines(fields: AqFields, vm_id: str):
    for host in fields.hostnames:
        try:
            aq_api.aq_manage(host, "domain", ConsumerConfig().aq_domain)
        except Exception as err:
            logger.error("Failed to manage in Aquilon: %s", err)
            openstack_api.update_metadata(
                fields.project_id, vm_id, {"AQ_STATUS": "FAILED"}
            )
            raise err
        try:
            aq_api.aq_make(host, fields)
        except Exception as err:
            logger.error("Failed to make in Aquilon: %s", err)
            openstack_api.update_metadata(
                fields.project_id, vm_id, {"AQ_STATUS": "FAILED"}
            )
            raise err


def _aq_create_host(firstip, machinename, vm_id: str, fields: AqFields):
    aq_api.create_host(
        fields.hostnames[0],
        machinename,
        firstip,
        fields.osname,
        fields.osversion,
    )  # osname needs to be valid otherwise it fails - also need to pass in sandbox
    openstack_api.update_metadata(
        fields.project_id, vm_id, {"AQ_MACHINENAME": machinename}
    )


def _aq_update_machine_nic(machinename):
    logger.debug("Updating Interfaces")
    try:
        aq_api.update_machine_interface(machinename, "eth0")
    except Exception as err:
        raise RuntimeError("Failed to set default interface") from err
    logger.debug("Creating Host")


def _aq_add_optional_nics(hostnames, machinename, message):
    logger.debug("Creating Interfaces2")
    for index, ip_addr in enumerate(message.get("payload").get("fixed_ips")):
        if index > 0:
            interfacename = "eth" + str(index)
            try:
                aq_api.add_machine_interface_address(
                    machinename,
                    ip_addr.get("address"),
                    interfacename,
                    # socket.gethostbyaddr(ip.get("address"))[0])
                    hostnames[0],
                )
            except Exception as err:
                raise RuntimeError("Failed to add machine interface address") from err


def _aq_add_first_nic(machinename, message):
    logger.debug("Creating Interfaces")
    for index, ip_addr in enumerate(message.get("payload").get("fixed_ips")):
        interfacename = "eth" + str(index)
        try:
            aq_api.add_machine_interface(
                machinename,
                ip_addr.get("vif_mac"),
                interfacename,
                # socket.gethostbyaddr(ip.get("address"))[0])
            )
        except Exception as err:
            raise RuntimeError("Failed to add machine interface") from err


def _aq_create_machine(hostnames, message):
    logger.debug("Creating machine")
    try:
        machine_name = aq_api.create_machine(
            message,
            hostnames[-1],
            ConsumerConfig().aq_prefix,
        )
    except Exception as err:
        raise RuntimeError("Failed to create machine") from err

    first_ip = message.get("payload").get("fixed_ips")[0].get("address")
    return first_ip, machine_name


def _add_hostname_to_metadata(fields: AqFields, vm_id):
    try:
        # add hostname(s) to metadata for use when capturing delete messages
        # as these messages do not contain ip information
        openstack_api.update_metadata(
            fields.project_id, vm_id, {"HOSTNAMES": ", ".join(fields.hostnames)}
        )
    except Exception as err:
        raise RuntimeError("Failed to update metadata") from err
    logger.debug("Building metadata")


def convert_hostnames(message):
    # convert VM ip address(es) into hostnames
    hostnames = []
    for ip_addr in message.get("payload").get("fixed_ips"):
        try:
            hostname = socket.gethostbyaddr(ip_addr.get("address"))[0]
            hostnames.append(hostname)
        except socket.herror:
            logger.info("No hostname found for ip %s", ip_addr.get("address"))
        except Exception:
            logger.error("Problem converting ip to hostname")
            raise
    if len(hostnames) > 1:
        logger.warning("There are multiple hostnames assigned to this VM")
    logger.debug("Hostnames: %s", hostnames)
    return hostnames


def on_message(message):
    raw_body = message.body
    body = json.loads(raw_body.decode("utf-8"))
    decoded = json.loads(body["oslo.message"])

    if not is_aq_message(decoded):
        logger.debug("Ignoring message: %s", decoded)
        return

    logger.debug("Got message: %s", raw_body)
    consume(decoded)
    message.ack()


def initiate_consumer():
    logger.debug("Initiating message consumer")
    # Ensure we have valid creds before trying to contact rabbit
    verify_kerberos_ticket()

    config = ConsumerConfig()

    host = config.rabbit_host
    port = config.rabbit_port
    login_user = config.rabbit_username
    login_pass = config.rabbit_password
    logger.debug(
        "Connecting to rabbit with: amqp://%s:<password>@%s:%s/", login_user, host, port
    )
    exchanges = ["nova"]

    login_str = f"amqp://{login_user}:{login_pass}@{host}:{port}/"
    with rabbitpy.Connection(login_str) as conn:
        with conn.channel() as channel:
            logger.debug("Connected to RabbitMQ")

            # Durable indicates that the queue will survive a broker restart
            queue = rabbitpy.Queue(channel, name="ral.info", durable=True)
            for exchange in exchanges:
                logger.debug("Binding to exchange: %s", exchange)
                queue.bind(exchange, routing_key="ral.info")

            # Consume the messages from generator
            message: rabbitpy.Message
            logger.debug("Starting to consume messages")
            for message in queue:
                on_message(message)
