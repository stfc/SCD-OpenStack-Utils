#!/usr/bin/python
import pika, json, aq_manage, sys, os
from ConfigParser import SafeConfigParser

try:
    config = SafeConfigParser()
    config.read("/etc/openstack-utils/consumer.ini")
    host = config.get("rabbit", "host")
    port = config.getint("rabbit", "port")
    login_user = config.get("rabbit", "login_user")
    login_pass = config.get("rabbit", "login_pass")
    exchanges = config.get("rabbit", "exchanges")
    exchanges = exchanges.split("\n")

    os.environ["OS_AUTH_URL"]=config.get("openstack","auth_url")
    os.environ["OS_PROJECT_ID"]=config.get("openstack","project_id")
    os.environ["OS_PROJECT_NAME"]=config.get("openstack","project_name")
    os.environ["OS_USER_DOMAIN_NAME"]=config.get("openstack","user_domain")
    os.environ["OS_USERNAME"]=config.get("openstack","username")
    os.environ["OS_PASSWORD"]=config.get("openstack","password")
    os.environ["OS_CACERT"]=config.get("openstack","cacert")
except Exception as e:
    print("Could not load config file.")
    print(e)
    sys.exit()

def on_message(channel, method, header, raw_body):
    body = raw_body.decode("utf-8")
    message = json.loads(json.loads(body)["oslo.message"])
    event = message.get("event_type")
    if event != "compute.metrics.update" and event != "compute.instance.exists":
        print(message.get("_context_user_name"))
        print(event)
    if event == "compute.instance.create.end":
        payload = message["payload"]
        aq_manage.vm_create(payload)
    elif event == "compute.instance.soft_delete.start":
        payload = message["payload"]
        aq_manage.vm_delete(payload)
    channel.basic_ack(delivery_tag=method.delivery_tag)

credentials = pika.PlainCredentials(login_user,login_pass)
parameters = pika.ConnectionParameters(host,
                                       port,
                                       "/",
                                       credentials,
                                       connection_attempts=10,
                                       retry_delay=2)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare("ral.info")
print(exchanges)
#consider making queue exclusive
for exchange in exchanges:
    channel.queue_bind("ral.info",
                       exchange,
                       "ral.info")
channel.basic_consume(on_message, "ral.info")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
connection.close()
