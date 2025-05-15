# Services

## Contents
- [What services are deployed?](#what-services-are-deployed)
- [How are services accessed?](#how-are-the-services-accessed)
- [What does each service do?](#what-does-each-service-do)
- [How do services communicate?](#how-do-services-communicate)

## What services are deployed?

![ChatOps Services](chatops_services.svg "Diagram of ChatOps Services")

## How are the services accessed?  

We are using sub-domains and a wildcard DNS record to access all services from
one address. The root URL is `(dev-)cloud-chatops.nubes.rl.ac.uk` and a 
sub-domain is prepended depending on what you are trying to access. Assuming 
you are accessing the production services, the below URLs will take you to the 
available services:

- (Grafana) https://grafana.cloud-chatops.nubes.rl.ac.uk 
- (Elastic Stack Kibana) https://kibana.cloud-chatops.nubes.rl.ac.uk
- (Prometheus) https://prometheus.cloud-chatops.nubes.rl.ac.uk
- (Alertmanager) https://alertmanager.cloud-chatops.nubes.rl.ac.uk
- (HAProxy stats) https://cloud-chatops.nubes.rl.ac.uk/stats
- (ChatOps Application) https://cloud-chatops.nubes.rl.ac.uk
- (ChatOps Specific URL) https://chatops.cloud-chatops.nubes.rl.ac.uk

Grafana is the only service implementing IRIS IAM login and other services use basic authentication.

## What does each service do?

### HAProxy

- Load balances traffic for the ChatOps application
- Uses layer 7 routing to navigate a user between services using sub-domains
- Acts as TLS termination between the internet and the private network

### ChatOps Application

- The Docker image being supported by this project which provides notifications
to Slack about open pull requests
- Multiple instances running for high availability

### Grafana

- Hosts visual dashboards that display the services' status from a Prometheus 
datasource
- View HAProxy stats such as the frequency of requests

### Prometheus

- Collects metrics from endpoints provided by Systemd-Exporter and cAdvisor
- Sends alerts to Alertmanager based on configured rules
- Provides a datasource to Grafana

### Alertmanager

- Manages alerts sent by Prometheus by forwarding them to Slack or a Mail server
- Groups duplicate alerts into single messages to prevent spam

### Elasticsearch

- Acts as a centralised log store for all services
- Provides a search engine to query for logs

### Kibana

- Provides a user interface to query Elasticsearch

### Logstash

- Receives logs from Filebeat and sends them to Elasticsearch
- Uses pipelines to filter and mutate messages before storing them in Elasticsearch

### Filebeat

- Reads log files of services and exports their contents to Logstash
- Uses regular expression patterns to concatenate multiline logs into single messages
- Runs on all nodes

### Systemd Exporter

- Provides a metrics endpoint for Prometheus with data about the systemd services on a node
- Runs on all nodes
- Used for Prometheus to alert when systemd services such as Grafana or Logstash go down

### cAdvisor

- Provides more useful container metrics than the Docker socket metrics endpoint
- Runs on only the ChatOps nodes
- Used for Prometheus to alert when the ChatOps containers go down

## How do services communicate?

All services communicate within the private network using HTTPS. 
Self-signed certificates are generated on the local Ansible host and copied to each service. 
HAProxy uses a Let's Encrypt
certificate for external traffic which is then terminated and re-encrypted with the service's self-signed certificate
before being sent out to the destination service. Individual services will also sign their own traffic with each other's
certificates.

See the below diagram for an example of external to internal communication:

![ChatOps External SSL](chatops_external_ssl.svg)

See the below diagram for an example of inter-service communication:

![ChatOps Internal SSL](chatops_internal_ssl.svg)