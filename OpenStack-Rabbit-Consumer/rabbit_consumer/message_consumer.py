import json
import logging
import socket

import rabbitpy

from rabbit_consumer import aq_api
from rabbit_consumer import openstack_api
from rabbit_consumer.aq_api import verify_kerberos_ticket
from rabbit_consumer.rabbit_consumer import RabbitConsumer
from rabbit_consumer.consumer_config import ConsumerConfig

logger = logging.getLogger(__name__)


def is_aq_message(message):
    """
    Check to see if the metadata in the message contains entries that suggest it
    is for an Aquilon VM.
    """

    logger.debug("Payload meta: %s" % message.get("payload").get("metadata"))

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

    logger.debug("Image meta: %s" % message.get("payload").get("image_meta"))

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

        logger.debug("Project Name: %s (%s)", project_name, project_id)
        logger.debug("VM Name: %s (%s) ", vm_name, vm_id)
        logger.debug("Username: %s", username)
        logger.debug("Hostnames: %s" + metadata.get("HOSTNAMES"))

        for host in metadata.get("HOSTNAMES").split(","):
            try:
                aq_api.delete_host(host)
            except Exception as e:
                logger.error("Failed to delete host: %s", e)
                openstack_api.update_metadata(
                    project_id, vm_id, {"AQ_STATUS": "FAILED"}
                )
                raise Exception("Failed to delete host")
            try:
                aq_api.del_machine_interface_address(host, "eth0", machinename)
            except Exception as e:
                raise Exception(
                    "Failed to delete interface address from machine  %s", e
                )

        try:
            aq_api.delete_machine(machinename)
        except Exception as e:
            raise Exception("Failed to delete machine")

        try:
            for host in metadata.get("HOSTNAMES").split(","):
                aq_api.reset_env(host)
        except Exception as e:
            logger.error("Failed to reset Aquilon configuration: %s", e)
            openstack_api.update_metadata(project_id, vm_id, {"AQ_STATUS": "FAILED"})
            raise Exception("Failed to reset Aquilon configuration")

        logger.info("Successfully reset Aquilon configuration")
        logger.info("=== Finished Aquilon deletion hook for VM %s ===", vm_name)


def _handle_create_machine(message):
    if is_aq_message(message):
        logger.info("=== Received Aquilon VM create message ===")

        project_name = message.get("_context_project_name")
        project_id = message.get("_context_project_id")
        vm_id = message.get("payload").get("instance_id")
        vm_name = message.get("payload").get("display_name")
        username = message.get("_context_user_name")

        hostnames = convert_hostnames(message, vm_name)

        logger.info("Project Name: %s (%s)", project_name, project_id)
        logger.info("VM Name: %s (%s) ", vm_name, vm_id)
        logger.info("Username: %s", username)
        logger.info("Hostnames: " + ", ".join(hostnames))

        try:
            # add hostname(s) to metadata for use when capturing delete messages
            # as these messages do not contain ip information
            openstack_api.update_metadata(
                project_id, vm_id, {"HOSTNAMES": ", ".join(hostnames)}
            )
        except Exception as e:
            logger.error("Failed to update metadata: %s", e)
            raise Exception("Failed to update metadata")
        logger.info("Building metadata")

        domain = get_metadata_value(message, "AQ_DOMAIN")
        sandbox = get_metadata_value(message, "AQ_SANDBOX")
        personality = get_metadata_value(message, "AQ_PERSONALITY")
        osversion = get_metadata_value(message, "AQ_OSVERSION")
        archetype = get_metadata_value(message, "AQ_ARCHETYPE")
        osname = get_metadata_value(message, "AQ_OS")

        vcpus = message.get("payload").get("vcpus")
        root_gb = message.get("payload").get("root_gb")
        memory_mb = message.get("payload").get("memory_mb")
        uuid = message.get("payload").get("instance_id")
        vmhost = message.get("payload").get("host")
        firstip = message.get("payload").get("fixed_ips")[0].get("address")

        logger.info("Creating machine")

        try:
            machinename = aq_api.create_machine(
                uuid,
                vmhost,
                vcpus,
                memory_mb,
                hostnames[-1],
                ConsumerConfig().aq_prefix,
            )
        except Exception as e:
            raise Exception("Failed to create machine: {0}".format(e))
        logger.info("Creating Interfaces")

        for index, ip in enumerate(message.get("payload").get("fixed_ips")):
            interfacename = "eth" + str(index)
            try:
                aq_api.add_machine_interface(
                    machinename,
                    ip.get("vif_mac"),
                    interfacename,
                    # socket.gethostbyaddr(ip.get("address"))[0])
                )
            except Exception as e:
                raise Exception("Failed to add machine interface: %s", e)
                logger.error("Failed to add machine interface %s", e)
        logger.info("Creating Interfaces2")

        for index, ip in enumerate(message.get("payload").get("fixed_ips")):
            if index > 0:
                interfacename = "eth" + str(index)
                try:
                    aq_api.add_machine_interface_address(
                        machinename,
                        ip.get("address"),
                        interfacename,
                        # socket.gethostbyaddr(ip.get("address"))[0])
                        hostnames[0],
                    )
                except Exception as e:
                    raise Exception("Failed to add machine interface address %s", e)
        logger.info("Updating Interfaces")

        try:
            aq_api.update_machine_interface(machinename, "eth0")
        except Exception as e:
            raise Exception("Failed to set default interface %s", e)
        logger.info("Creating Host")

        try:
            aq_api.create_host(
                hostnames[0],
                machinename,
                sandbox,
                firstip,
                domain,
                osname,
                osversion,
            )  # osname needs to be valid otherwise it fails - also need to pass in sandbox
        except Exception as e:
            logger.error("Failed to create host: %s", e)
            raise Exception(
                "IP Address already exists on %s, using that machine instead", e
            )
            logger.error(
                "IP Address already exists on %s, using that machine instead",
                newmachinename,
            )
            raise Exception("Failed to create host: %s", e)

        openstack_api.update_metadata(
            project_id, vm_id, {"AQ_MACHINENAME": machinename}
        )
        logger.info("Domain: %s", domain)
        logger.info("Sandbox: %s", sandbox)
        logger.info("Personality: %s", personality)
        logger.info("OS Version: %s", osversion)
        logger.info("Archetype: %s", archetype)
        logger.info("OS Name: %s", osname)

        # as the machine may have been assigned more that one ip address,
        # apply the aquilon configuration to all of them
        for host in hostnames:

            try:
                if sandbox:
                    aq_api.aq_manage(host, "sandbox", sandbox)
                else:
                    aq_api.aq_manage(host, "domain", domain)
            except Exception as e:
                logger.error("Failed to manage in Aquilon: %s", e)
                openstack_api.update_metadata(
                    project_id, vm_id, {"AQ_STATUS": "FAILED"}
                )
                raise Exception("Failed to set Aquilon configuration %s", e)
            try:
                aq_api.aq_make(host, personality, osversion, archetype, osname)
            except Exception as e:
                logger.error("Failed to make in Aquilon: %s", e)
                openstack_api.update_metadata(
                    project_id, vm_id, {"AQ_STATUS": "FAILED"}
                )
                raise Exception("Failed to set Aquilon configuration %s", e)

        logger.info("Successfully applied Aquilon configuration")
        openstack_api.update_metadata(project_id, vm_id, {"AQ_STATUS": "SUCCESS"})

        logger.info("=== Finished Aquilon creation hook for VM " + vm_name + " ===")


def convert_hostnames(message, vm_name):
    # convert VM ip address(es) into hostnames
    hostnames = []
    for ip in message.get("payload").get("fixed_ips"):
        try:
            hostname = socket.gethostbyaddr(ip.get("address"))[0]
            hostnames.append(hostname)

        except Exception as e:
            logger.error("Problem converting ip to hostname", e)
    #        raise Exception("Problem converting ip to hostname")
    if len(hostnames) > 1:
        logger.warning("There are multiple hostnames assigned to this VM")
    elif len(hostnames) < 1:
        hostname = vm_name + ".novalocal"
        hostnames.append(hostname)
    logger.debug("Hostnames: " + ", ".join(hostnames))
    return hostnames


def on_message(method, header, raw_body):
    logging.debug("Got message: %s", raw_body)
    body = json.loads(raw_body.decode("utf-8"))
    message = json.loads(body["oslo.message"])

    try:
        consume(message)
    except Exception as e:
        logger.error("Something went wrong parsing the message: %s", e)
        logger.error(str(message))


def initiate_consumer():
    logger.info("Initiating message consumer")
    # Ensure we have valid creds before trying to contact rabbit
    verify_kerberos_ticket()

    config = ConsumerConfig()

    host = config.rabbit_host
    port = config.rabbit_port
    login_user = config.rabbit_username
    login_pass = config.rabbit_password
    login_str = f"amqp://{login_user}:{login_pass}@{host}:{port}/"

    exchanges = RabbitConsumer.config.get("rabbit", "exchanges").split(",")

    with rabbitpy.Connection(login_str) as conn:
        with conn.channel() as channel:
            logger.info("Connected to RabbitMQ")

            # Durable indicates that the queue will survive a broker restart
            queue = rabbitpy.Queue(channel, name="ral.info", durable=True)
            for exchange in exchanges:
                logger.debug("Binding to exchange: %s", exchange)
                queue.bind(exchange, routing_key="ral.info")

            # Consume the messages from generator
            message: rabbitpy.Message
            logger.info("Starting to consume messages")
            for message in queue:
                on_message(
                    method=message.method,
                    header=message.properties,
                    raw_body=message.body,
                )
                message.ack()
