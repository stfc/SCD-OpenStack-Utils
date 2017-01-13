#!/usr/bin/python
import pika, json, aq_manage, sys
from ConfigParser import SafeConfigParser

try:
    config = SafeConfigParser()
    config.read("consumer.ini")
    host = config.get("consumer", "host")
    port = config.getint("consumer", "port")
    login_user = config.get("consumer", "login_user")
    login_pass = config.get("consumer", "login_pass")
    exchanges = config.get("consumer", "exchanges")
    exchanges = exchanges.split("\n")
except:
    print("Could not load config file.")
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

"http://rabbit1.nubes.rl.ac.uk:15672/api/queues/%2F/ral.info"

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
for exchange in exchanges:
    print(exchange)
    channel.queue_bind("ral.info",
                       exchange,
                       "ral.info")
channel.basic_consume(on_message, "ral.info")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
connection.close()
