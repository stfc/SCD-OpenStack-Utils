import json
import logging
import re
import socket
import sys

import pika

from rabbit_consumer import aq_api
from rabbit_consumer import openstack_api
from rabbit_consumer.common import RabbitConsumer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logging.basicConfig(
    format="[%(levelname)s:%(filename)s:%(funcName)s():%(lineno)d] %(message)s"
)
logger = logging.getLogger("tcpserver")


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
    prefix = RabbitConsumer.config.get("aquilon", "prefix")
    if event == "compute.instance.create.end":
        if is_aq_message(message):
            logger.info("=== Received Aquilon VM create message ===")

            project_name = message.get("_context_project_name")
            project_id = message.get("_context_project_id")
            vm_id = message.get("payload").get("instance_id")
            vm_name = message.get("payload").get("display_name")
            username = message.get("_context_user_name")

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
            logger.info("Hostnames: " + ", ".join(hostnames))

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
                    uuid, vmhost, vcpus, memory_mb, hostname, prefix
                )
            except Exception as e:
                raise Exception("Failed to create machine {0}".format(e))
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
                    raise Exception("Failed to add machine interface %s", e)
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
                    archetype,
                    domain,
                    personality,
                    osname,
                    osversion,
                )  # osname needs to be valid otherwise it fails - also need to pass in sandbox
            except Exception as e:
                logger.error("Failed to create host: %s", e)
                newmachinename = re.search("vm-openstack-[A-Za-z]*-[0-9]*", e).group(1)
                raise Exception(
                    "IP Address already exists on %s, using that machine instead",
                    newmachinename,
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
                        aq_api.aq_manage(hostname, "sandbox", sandbox)
                    else:
                        aq_api.aq_manage(hostname, "domain", domain)
                except Exception as e:
                    logger.error("Failed to manage in Aquilon: %s", e)
                    openstack_api.update_metadata(
                        project_id, vm_id, {"AQ_STATUS": "FAILED"}
                    )
                    raise Exception("Failed to set Aquilon configuration %s", e)
                try:
                    aq_api.aq_make(hostname, personality, osversion, archetype, osname)
                except Exception as e:
                    logger.error("Failed to make in Aquilon: %s", e)
                    openstack_api.update_metadata(
                        project_id, vm_id, {"AQ_STATUS": "FAILED"}
                    )
                    raise Exception("Failed to set Aquilon configuration %s", e)

            logger.info("Successfully applied Aquilon configuration")
            openstack_api.update_metadata(project_id, vm_id, {"AQ_STATUS": "SUCCESS"})

            logger.info("=== Finished Aquilon creation hook for VM " + vm_name + " ===")

    if event == "compute.instance.delete.start":
        if is_aq_message(message):
            logger.info("=== Received Aquilon VM delete message ===")

            project_name = message.get("_context_project_name")
            project_id = message.get("_context_project_id")
            vm_id = message.get("payload").get("instance_id")
            vm_name = message.get("payload").get("display_name")
            username = message.get("_context_user_name")
            metadata = message.get("payload").get("metadata")
            machinename = message.get("payload").get("metadata").get("AQ_MACHINENAME")

            logger.info("Project Name: %s (%s)", project_name, project_id)
            logger.info("VM Name: %s (%s) ", vm_name, vm_id)
            logger.info("Username: %s", username)
            logger.info("Hostnames: %s", metadata.get("HOSTNAMES"))

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
                openstack_api.update_metadata(
                    project_id, vm_id, {"AQ_STATUS": "FAILED"}
                )
                raise Exception("Failed to reset Aquilon configuration")

            logger.info("Successfully reset Aquilon configuration")
            logger.info("=== Finished Aquilon deletion hook for VM %s ===", vm_name)


def on_message(channel, method, header, raw_body):
    body = json.loads(raw_body.decode("utf-8"))
    message = json.loads(body["oslo.message"])

    try:
        consume(message)
    except Exception as e:
        logger.error("Something went wrong parsing the message: %s", e)
        logger.error(str(message))

    # remove the message from the queue
    channel.basic_ack(delivery_tag=method.delivery_tag)


def initiate_consumer():
    logger.info("Initiating message consumer")
    prefix = RabbitConsumer.config.get("aquilon", "prefix")
    host = RabbitConsumer.config.get("rabbit", "host")
    port = RabbitConsumer.config.getint("rabbit", "port")
    login_user = RabbitConsumer.config.get("rabbit", "login_user")
    login_pass = RabbitConsumer.config.get("rabbit", "login_pass")
    exchanges = RabbitConsumer.config.get("rabbit", "exchanges").split(",")

    credentials = pika.PlainCredentials(login_user, login_pass)
    parameters = pika.ConnectionParameters(
        host, port, "/", credentials, connection_attempts=10, retry_delay=2
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare("ral.info")

    for exchange in exchanges:
        channel.queue_bind("ral.info", exchange, "ral.info")

    channel.basic_consume(on_message, "ral.info")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()
        sys.exit(0)
    except Exception as e:
        logger.error("Something went wrong with the pika message consumer %s", e)
        connection.close()
        raise e
