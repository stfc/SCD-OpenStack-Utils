import json
import logging
from typing import Optional, List

import rabbitpy

from rabbit_consumer import aq_api
from rabbit_consumer import openstack_api
from rabbit_consumer.aq_api import verify_kerberos_ticket
from rabbit_consumer.consumer_config import ConsumerConfig
from rabbit_consumer.openstack_address import OpenstackAddress
from rabbit_consumer.os_descriptions.os_descriptions import OsDescription
from rabbit_consumer.rabbit_message import RabbitMessage
from rabbit_consumer.vm_data import VmData

logger = logging.getLogger(__name__)


def is_aq_managed_image(rabbit_message: RabbitMessage) -> Optional[OsDescription]:
    """
    Check to see if the metadata in the message contains entries that suggest it
    is for an Aquilon VM.
    """

    image_name = rabbit_message.payload.image_name
    if not image_name:
        logger.debug("No image_name found in payload")
        return None

    try:
        return OsDescription.from_image_name(image_name)
    except ValueError:
        logger.debug("Image name %s does not match an Aquilon image name", image_name)
        return None


def consume(message: RabbitMessage) -> None:
    """
    Consumes a message from the rabbit queue and calls the appropriate
    handler based on the event type.
    """
    if not is_aq_managed_image(message):
        logger.info("Skipping non Aquilon managed image")
        return

    if message.event_type == "compute.instance.create.end":
        handle_create_machine(message)

    if message.event_type == "compute.instance.delete.start":
        handle_machine_delete(message)


def handle_create_machine(rabbit_message: RabbitMessage) -> None:
    """
    Handles the creation of a machine in Aquilon. This includes
    creating the machine, adding the nics, and managing the host.
    """
    logger.info("=== Received Aquilon VM create message ===")
    _print_debug_logging(rabbit_message)

    vm_data = VmData.from_message(rabbit_message)
    os_details = is_aq_managed_image(rabbit_message)
    network_details = openstack_api.get_server_networks(vm_data)

    if not network_details or not network_details[0].hostname:
        vm_name = rabbit_message.payload.vm_name
        logger.info("Skipping novalocal only host: %s", vm_name)
        return

    # Configure networking
    machine_name = aq_api.create_machine(rabbit_message, vm_data)
    aq_api.add_machine_nics(machine_name, network_details)
    aq_api.set_interface_bootable(machine_name, "eth0")

    # Manage host in Aquilon
    aq_api.create_host(os_details, network_details, machine_name)
    aq_api.aq_manage(network_details)
    aq_api.aq_make(network_details, os_details)

    add_hostname_to_metadata(vm_data, network_details)
    openstack_api.update_metadata(vm_data, {"AQ_STATUS": "SUCCESS"})

    logger.info(
        "=== Finished Aquilon creation hook for VM %s ===", vm_data.virtual_machine_id
    )


def _print_debug_logging(rabbit_message: RabbitMessage) -> None:
    """
    Prints debug logging for the Aquilon message.
    """
    vm_data = VmData.from_message(rabbit_message)
    logger.debug(
        "Project Name: %s (%s)", rabbit_message.project_name, vm_data.project_id
    )
    logger.debug(
        "VM Name: %s (%s) ", rabbit_message.payload.vm_name, vm_data.virtual_machine_id
    )
    logger.debug("Username: %s", rabbit_message.user_name)


def handle_machine_delete(rabbit_message: RabbitMessage) -> None:
    """
    Handles the deletion of a machine in Aquilon. This includes
    deleting the machine and the host.
    """
    logger.info("=== Received Aquilon VM delete message ===")
    _print_debug_logging(rabbit_message)

    vm_data = VmData.from_message(rabbit_message)
    network_data = openstack_api.get_server_networks(vm_data)

    if not network_data or not network_data[0].hostname:
        vm_name = rabbit_message.payload.vm_name
        logger.debug("No hostnames found for %s, skipping delete", vm_name)
        return

    for host in network_data:
        aq_api.delete_host(host.hostname)

    aq_api.delete_machine(rabbit_message.payload.metadata.machine_name)

    logger.info(
        "=== Finished Aquilon deletion hook for VM %s ===", vm_data.virtual_machine_id
    )


def add_hostname_to_metadata(
    fields: VmData, network_details: List[OpenstackAddress]
) -> None:
    """
    Adds the hostname to the metadata of the VM.
    """
    if not openstack_api.check_machine_exists(fields):
        # User has likely deleted the machine since we got here
        logger.warning(
            "Machine %s does not exist, skipping metadata update",
            fields.virtual_machine_id,
        )
        return

    hostnames = [i.hostname for i in network_details]
    metadata = {"HOSTNAMES": ",".join(hostnames)}
    openstack_api.update_metadata(fields, metadata)


def on_message(message) -> None:
    """
    Deserializes the message and calls the consume function on message.
    """
    raw_body = message.body
    body = json.loads(raw_body.decode("utf-8"))
    decoded = RabbitMessage.from_json(body["oslo.message"])

    if not is_aq_managed_image(decoded):
        logger.debug("Ignoring message: %s", decoded)
        return

    logger.debug("Got message: %s", raw_body)
    consume(decoded)
    message.ack()


def initiate_consumer() -> None:
    """
    Initiates the message consumer and starts consuming messages in a loop.
    This includes setting up the rabbit connection and channel.
    """
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
