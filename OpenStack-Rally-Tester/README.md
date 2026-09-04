# Rally Tester Script

This script scrapes outputted task reports of rally metrics and feeds them to influxdb

## Prerequisites
- An InfluxDB server running HTTPs (using self-signed certs)
- A Rally VM that is generating reports - that we will deploy this script onto

## Installation

setup a python3 virtual environment
```commandline
dnf install python3.12 
python3.12 -m venv opt/extract-rally-venv
```

## Developer Notes - WIP

several bash scripts exist in aquilon that would be better served to be moved here
as those bash scripts reference this python script. Changing the python script here, 
will require changing the bash scripts - it would be much easier if they were all managed from a central source

if placed here, we can run CI/CD jobs against them 

TODO: tests
