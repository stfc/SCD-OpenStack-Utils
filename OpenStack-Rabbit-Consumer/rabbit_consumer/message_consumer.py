import json
import logging
from typing import Optional, List

import rabbitpy

from rabbit_consumer import aq_api
from rabbit_consumer import openstack_api
from rabbit_consumer.aq_api import verify_kerberos_ticket
from rabbit_consumer.consumer_config import ConsumerConfig
from rabbit_consumer.image_metadata import ImageMetadata
from rabbit_consumer.openstack_address import OpenstackAddress
from rabbit_consumer.rabbit_message import RabbitMessage, MessageEventType
from rabbit_consumer.vm_data import VmData

logger = logging.getLogger(__name__)
SUPPORTED_MESSAGE_TYPES = {
    "create": "compute.instance.create.end",
    "delete": "compute.instance.delete.start",
}


def is_aq_managed_image(rabbit_message: RabbitMessage) -> Optional[ImageMetadata]:
    """
    Check to see if the metadata in the message contains entries that suggest it
    is for an Aquilon VM.
    """
    image = openstack_api.get_image_name(VmData.from_message(rabbit_message))
    image_meta = ImageMetadata.from_dict(image.metadata)

    if not image_meta:
        logger.debug("Skipping non-Aquilon image: %s", image.name)
        return None
    return image_meta


def consume(message: RabbitMessage) -> None:
    """
    Consumes a message from the rabbit queue and calls the appropriate
    handler based on the event type.
    """
    if message.event_type == SUPPORTED_MESSAGE_TYPES["create"]:
        handle_create_machine(message)

    elif message.event_type == SUPPORTED_MESSAGE_TYPES["delete"]:
        handle_machine_delete(message)

    else:
        raise ValueError(f"Unsupported message type: {message.event_type}")


def delete_machine(addresses: List[OpenstackAddress]):
    for address in addresses:
        if aq_api.check_host_exists(address.hostname):
            logger.info("Host exists for %s. Deleting old", address.hostname)
            aq_api.delete_host(address.hostname)

        machine_name = aq_api.search_machine(address.mac_addr)
        if not machine_name:
            # Nothing else to do at this point
            return

        logger.info("Machine exists for MAC: %s. Deleting old", address.mac_addr)
        machine_details = aq_api.get_machine_details(machine_name)

        # We have to do this manually because AQ has neither a:
        # - Just delete the machine please
        # - Delete this if it exists
        # So alas we have to do everything by hand, whilst adhering to random rules
        # of deletion orders which it enforces...

        if address.addr in machine_details:
            aq_api.delete_address(address, machine_name)
        if address.mac_addr in machine_details:
            aq_api.delete_interface(address)
        aq_api.delete_machine(machine_name)


def check_machine_valid(rabbit_message: RabbitMessage) -> bool:
    """
    Checks to see if the machine is valid for creating in Aquilon.
    """
    vm_data = VmData.from_message(rabbit_message)
    if not openstack_api.check_machine_exists(vm_data):
        # User has likely deleted the machine since we got here
        logger.warning(
            "Machine %s does not exist, skipping creation", vm_data.virtual_machine_id
        )
        return False

    if not is_aq_managed_image(rabbit_message):
        logger.debug("Ignoring non AQ Image: %s", rabbit_message)
        return False

    return True


def handle_create_machine(rabbit_message: RabbitMessage) -> None:
    """
    Handles the creation of a machine in Aquilon. This includes
    creating the machine, adding the nics, and managing the host.
    """
    logger.info("=== Received Aquilon VM create message ===")
    _print_debug_logging(rabbit_message)

    if not check_machine_valid(rabbit_message):
        return

    vm_data = VmData.from_message(rabbit_message)

    image_meta = is_aq_managed_image(rabbit_message)
    network_details = openstack_api.get_server_networks(vm_data)

    if not network_details or not network_details[0].hostname:
        vm_name = rabbit_message.payload.vm_name
        logger.info("Skipping novalocal only host: %s", vm_name)
        return

    delete_machine(network_details)

    # Configure networking
    machine_name = aq_api.create_machine(rabbit_message, vm_data)
    aq_api.add_machine_nics(machine_name, network_details)
    aq_api.set_interface_bootable(machine_name, "eth0")

    # Manage host in Aquilon
    aq_api.create_host(image_meta, network_details, machine_name)

    aq_api.aq_manage(network_details, image_meta)
    aq_api.aq_make(network_details, image_meta)

    add_hostname_to_metadata(vm_data, network_details)

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
    logger.info(
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

    delete_machine(addresses=network_data)

    logger.info(
        "=== Finished Aquilon deletion hook for VM %s ===", vm_data.virtual_machine_id
    )


def add_hostname_to_metadata(
    vm_data: VmData, network_details: List[OpenstackAddress]
) -> None:
    """
    Adds the hostname to the metadata of the VM.
    """
    if not openstack_api.check_machine_exists(vm_data):
        # User has likely deleted the machine since we got here
        logger.warning(
            "Machine %s does not exist, skipping metadata update",
            vm_data.virtual_machine_id,
        )
        return

    hostnames = [i.hostname for i in network_details]
    metadata = {"HOSTNAMES": ",".join(hostnames), "AQ_STATUS": "SUCCESS"}
    openstack_api.update_metadata(vm_data, metadata)


def on_message(message: rabbitpy.Message) -> None:
    """
    Deserializes the message and calls the consume function on message.
    """
    raw_body = message.body
    logger.debug("New message: %s", raw_body)

    body = json.loads(raw_body.decode("utf-8"))["oslo.message"]
    parsed_event = MessageEventType.from_json(body)
    if parsed_event.event_type not in SUPPORTED_MESSAGE_TYPES.values():
        logger.info("Ignoring event_type: %s", parsed_event.event_type)
        message.ack()
        return

    decoded = RabbitMessage.from_json(body)
    logger.debug("Decoded message: %s", decoded)

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
