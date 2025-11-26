# IRISCAST Tools

> [!Warning]
> This package is deprecated and is not supported.

A python package that bundlels together a collection of energy usage monitoring scripts to be run on cloud hypervisors.

These scripts will collect power usage data using IPMI.

This package is intended to be installed onto HVs and a cronjob written to run this every 15mins to populate a csv - which can be read by filebeat/fluentd to a datastore.

## Installation

```bash
pip install "iriscasttools @ git+https://github.com/stfc/SCD-OpenStack-Utils.git"
```

## Usage

Run as a cron job:
```
python3 -m iriscasttols --as-csv >> /var/cache/iriscast/ipmi-stats-$(date -I).csv

```
