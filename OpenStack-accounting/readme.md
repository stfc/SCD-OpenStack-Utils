# TheCount


## Prerequisites

The following packages are required:
 - python-ConfigParser
 - python3-requests
 - python36-sqlalchemy
 - python36-PyMySQL

A database user with read access to the relevant databases for each OpenStack component you are accounting for

## Installation

Copy the scripts into `/usr/local/sbin` as shown in this repo
Create a config file with a database connection string in the format shown in `/etc/thecount/thecount.conf.example` in `/etc/thecount/thecount.conf`
Create the stored procedures in the `sql` directory appropriate db.

## Use

`now-accounting.sh` generates accounting for the last 24 hours - recommend setting up a cron to run this at midnight
`past-accounting.sh` takes a start date and an end date in the format "%Y-%m-%d %H:%M" to generate accounting for past usage where possible
`*-extract_accounting.py` takes a start date and an end date in the format "%Y-%m-%d %H:%M" to generate accounting for that component
