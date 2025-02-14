#!/bin/bash


set -e

openstack compute service list --long -f yaml > compute_service.yaml

openstack hypervisor list --long -f yaml > hypervisor.yaml

openstack ip availability show 0dc30001-edfb-4137-be76-8e51f38fd650 -f yaml > fip.yaml

openstack server list --all-projects --limit -1 -f yaml > server.yaml


python3 format_raw_data.py