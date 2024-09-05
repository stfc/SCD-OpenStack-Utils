# SCD OpenStack Utilities

## MonitoringTools

Monitoring Tools to collect vm stats for things such as influxDB. 
[More Here](MonitoringTools/)

## OpenStack-AD-Migrate

Copies user references from an LDAP group to an OpenStack project.
[More Here](OpenStack-AD-Migrate/)

### Usage
`./migrate.py <target groups file>`

## OpenStack-Rabbit-Consumer

The script will monitor the rabbit consumers, and automatically register machines
with the configuration management tool.
[More Here](OpenStack-Rabbit-Consumer/)

## OpenStack-Rally-Tester

Allows for automation for openstack resources, ensuring they run automatically with no errors. 
Allowing for automated testing to be done for Openstack
[More Here](OpenStack-Rally-Tester/)

## OpenStack-SecurityGroup-Create-Project

Adds ability to help manage security groups for a project.
[More Here](OpenStack-SecurityGroup-Create-Project/usr/local/bin/)

## Openstack-accounting

Makes a database user with read access to the relevant databases for each OpenStack component you are accounting for.
[More Here](OpenStack-accounting/)

## OpenStack_get_username

CGI script providing a simple method for obtaining the name of the creating user for any given instance ID.
[More Here](OpenStack_get_username/var/www/cgi-bin/)

## OpenStack_irisiam_mapper

CGI Script for mapping a project ID found in the instance metadata to any IRIS IAM groups that have access to this project
[More Here](OpenStack_irisiam_mapper/var/www/cgi-bin/)

## aq_zombie_finder

A Python script that when run returns a list of Cloud VMs that no longer exist, and should be investigated to be removed from Aquilon, as well as returning a list of machines using an "-aq" image that aren't being managed by Aquilon.
[More Here](aq_zombie_finder/)

## dns_entry_checker

A Python script that when run, create 4 files: one listing IP addresses that don't match their DNS name, one listing the IPs of DNS names that don't go to the correct IP, one listing IPs missing DNS names and one listing the gaps in the IP list.
[More Here](dns_entry_checker/)

## gpu_benchmark

This script is used to benchmark the GPU performance of a machine. It is based on the Phoronix Test Suite and will run a number of benchmarks automatically.
The script is designed to be run on a machine with a GPU, and will run with the specified number of GPUs (default 1).
[More Here](gpu_benchmark/)

## grafana_monitoring

This script is used to deploy a grafana container using a docker container, with Iris IAM login included and connection to database.
The env.sh file should be configured before running.
[Move Here](grafana_monitoring/)

## iris casttools

Scripts for collecting metrics for cloud energy collection to be displayed using monitoring softwares.
[More Here](iriscasttools/)

## jsm_metric_collection

A Python script that when run, creates 2 files: A CSV containing JSM metrics and an XLSX file generated from that CSV file.
[More Here](jsm_metric_collection/)

## prometheus_ip_script

A script used to generate prometheus configs including IP lists.
[More Here](prometheus_ip_script/)

## prometheus_query_to_csv

This script collects data from Prometheus and writes it to a CSV file.
[More Here](prometheus_query_to_csv/)

## pynetbox_query

A Python package to bulk upload systems data to Netbox from files creating devices and interfaces.
[More Here](pynetbox_query/)

## reverse_ssl_cert_chain

A Python script to reverse the SSL certificate chain order. For example, a certificate as CA -> Root would output as Root -> CA.
[More Here](reverse_ssl_cert_chain/)

## terraform_provisioning

One terraform script to create a private network on openstack along with a router and a subnet and one to deploy a load balancing application.
[More Here](terraform_provisioning/)

## word_cloud_generator

A Python script that when run, creates a filter word cloud from the summary of tickets over a time period.
[More Here](word_cloud_generator/)

