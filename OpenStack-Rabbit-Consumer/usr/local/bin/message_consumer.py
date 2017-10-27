import sys
import pika
import json
import socket
import logging

import common
import openstack_api
import aq_api

logger = logging.getLogger(__name__)


def is_aq_message(message):
    """
    Check to see if the metadata in the message contains entries that suggest it
    is for an Aquilon VM.
    """
    metadata = message.get("payload").get("metadata")
    print(metadata)
    if metadata:
        if set(metadata.keys()).intersection(['AQ_DOMAIN', 'AQ_SANDBOX', 'AQ_OSVERSION', 'AQ_PERSONALITY', 'AQ_ARCHETYPE', 'AQ_OS']):
            return True
    if metadata:
        if set(metadata.keys()).intersection(['aq_domain', 'aq_sandbox', 'aq_osversion', 'aq_personality', 'aq_archetype', 'aq_os']):
            return True
    metadata = message.get("payload").get("image_meta")
    print(metadata)
    if metadata:
        if set(metadata.keys()).intersection(['AQ_DOMAIN', 'AQ_SANDBOX', 'AQ_OSVERSION', 'AQ_PERSONALITY', 'AQ_ARCHETYPE', 'AQ_OS']):
            return True
    if metadata:
        if set(metadata.keys()).intersection(['aq_domain', 'aq_sandbox', 'aq_osversion', 'aq_personality', 'aq_archetype', 'aq_os']):
            return True
   
    return False

def get_AQ_value(message,key):
    returnstring = None
    returnstring = message.get("payload").get("metadata").get(key)
    if (returnstring == None):
        returnstring = message.get("payload").get("image_meta").get(key)
        if (returnstring == None):
            returnstring = message.get("payload").get("metadata").get(key.lower())
            if (returnstring == None):
                returnstring = message.get("payload").get("image_meta").get(key.lower())
    return returnstring


def consume(message):
    event = message.get("event_type")
    print (event)
    if event == "compute.instance.create.end":
        print (message)
        if is_aq_message(message):
            print("=== Received Aquilon VM create message ===")
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
                    hostnames.append(socket.gethostbyaddr(ip.get("address"))[0])
                except Exception as e:
                    logger.error("Problem converting ip to hostname" + str(e))
                    raise Exception("Problem converting ip to hostname")

            if len(hostnames) > 1:
                logger.warn("There are multiple hostnames assigned to this VM")

            logger.info("Project Name: %s (%s)" % (project_name, project_id))
            logger.info("VM Name: %s (%s) " % (vm_name, vm_id))
            logger.info("Username: " + username)
            logger.info("Hostnames: " + ', '.join(hostnames))

            try:
                # add hostname(s) to metadata for use when capturing delete messages
                # as these messages do not contain ip information
                openstack_api.update_metadata(project_id, vm_id, {"HOSTNAMES" : ', '.join(hostnames)})
            except Exception as e:
                logger.error("Failed to update metadata: " + str(e))
                raise Exception("Failed to update metadata")

            print (message.get("payload"))
            domain = get_AQ_value(message,"AQ_DOMAIN")
            sandbox =   get_AQ_value(message,"AQ_SANDBOX")
            personality =  get_AQ_value(message,"AQ_PERSONALITY")
            osversion =  get_AQ_value(message,"AQ_OSVERSION")
            archetype =  get_AQ_value(message,"AQ_ARCHETYPE")
            osname =  get_AQ_value(message,"AQ_OSNAME")
 


            print("Domain: %s" % domain)
            print("Sandbox: %s" % sandbox)
            print("Personality: %s" % personality)
            print("OS Version: %s" % osversion)
            print("Archetype: %s" % archetype)
            print("OS Name: %s" % osname)

            logger.info("Domain: %s" % domain)
            logger.info("Sandbox: %s" % sandbox)
            logger.info("Personality: %s" % personality)
            logger.info("OS Version: %s" % osversion)
            logger.info("Archetype: %s" % archetype)
            logger.info("OS Name: %s" % osname)

            try:
                # as the machine may have been assigned more that one ip address,
                # apply the aquilon configuration to all of them
                for host in hostnames:
                    aq_api.vm_create(host, domain, sandbox, personality, osversion, archetype, osname)
            except Exception as e:
                logger.error("Failed to set Aquilon configuration: " + str(e))
                openstack_api.update_metadata(project_id, vm_id, {"AQ_STATUS" : "FAILED"})
                raise Exception("Failed to set Aquilon configuration")

            logger.info("Successfully applied Aquilon configuration")
            openstack_api.update_metadata(project_id, vm_id, {"AQ_STATUS" : "SUCCESS"})

            logger.info("=== Finished Aquilon creation hook for VM " + vm_name + " ===")


    if event == "compute.instance.delete.start":
        print (message)
        if is_aq_message(message):
            logger.info("=== Received Aquilon VM delete message ===")

            project_name = message.get("_context_project_name")
            project_id = message.get("_context_project_id")
            vm_id = message.get("payload").get("instance_id")
            vm_name = message.get("payload").get("display_name")
            username = message.get("_context_user_name")
            metadata = message.get("payload").get("metadata")

            logger.info("Project Name: %s (%s)" % (project_name, project_id))
            logger.info("VM Name: %s (%s) " % (vm_name, vm_id))
            logger.info("Username: " + username)
            logger.info("Hostnames: %s" % metadata.get('HOSTNAMES'))

            try:
                for host in metadata.get('HOSTNAMES').split(','):
                    aq_api.vm_delete(host)
            except Exception as e:
                logger.error("Failed to reset Aquilon configuration: " + str(e))
                openstack_api.update_metadata(project_id, vm_id, {"AQ_STATUS" : "FAILED"})
                raise Exception("Failed to reset Aquilon configuration")

            logger.info("Successfully reset Aquilon configuration")
            logger.info("=== Finished Aquilon deletion hook for VM " + vm_name + " ===")


def on_message(channel, method, header, raw_body):
    body = json.loads(raw_body.decode("utf-8"))
    message = json.loads(body["oslo.message"])

    try:
        consume(message)
    except Exception as e:
        logger.error("Something went wrong parsing the message: " + str(e))
        logger.error(str(message))

    # remove the message from the queue
    channel.basic_ack(delivery_tag=method.delivery_tag)


def initiate_consumer():
    logger.info("Initiating message consumer")

    host = common.config.get("rabbit", "host")
    port = common.config.getint("rabbit", "port")
    login_user = common.config.get("rabbit", "login_user")
    login_pass = common.config.get("rabbit", "login_pass")
    exchanges = common.config.get("rabbit", "exchanges").split(",")

    credentials = pika.PlainCredentials(login_user, login_pass)
    parameters = pika.ConnectionParameters(host, port, "/", credentials,
                                           connection_attempts=10,
                                           retry_delay=2)

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
        logger.error("Something went wrong with the pika message consumer " + str(e))
        connection.close()
        raise e
