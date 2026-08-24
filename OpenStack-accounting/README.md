# Thecount - fetch, calculate and store cloud accounting data  

## Prerequisites

A VM/system/device with docker installed
1. must have access to an Openstack DB - with an accounting user setup - to fetch relevant openstack data. 
User with read access to the relevant databases for each OpenStack component you are accounting for - right now:
   - cinder
   - manila
   - nova
   - glance

2. must have access to an influxdb TSDB - for storing parsed accounting data and setup a user with write permissions

## Setting up SQL Procedures

under `sql` folder, several `.sql` files exist that set out SQL procedure code that can be saved onto the database 
and can be executed whenever needed to collect accounting data

to apply login to mysql:
`mysql -u admin -p mypass`
run:
`USE cinder`
`SOURCE /sql/cinder_get_accounting_data.sql;`

make sure you set the correct db before applying the sql file

Then you need to set permissions for accounting user  
`mysql -u admin -p <pass>`

create user - repeat for each monitoring node and where `accounting-db` is the user
`CREATE USER 'accounting-db'@'host.example.com' IDENTIFIED BY 'StrongPasswordHere!';`

set permissions for each db - repeat for each monitoring node

```
GRANT SELECT, EXECUTE ON `keystone`.* TO `accounting-db`@`host.example.com`;
GRANT SELECT, EXECUTE ON `nova`.* TO `accounting-db`@`host.example.com`;
GRANT SELECT, EXECUTE ON `glance`.* TO `accounting-db`@`host.example.com`;
GRANT SELECT, EXECUTE ON `cinder`.* TO `accounting-db`@`host.example.com`;
GRANT SELECT, EXECUTE ON `manila`.* TO `accounting-db`@`host.example.com`;
GRANT SELECT, EXECUTE ON `nova_api`.* TO `accounting-db`@`host.example.com`;
GRANT SELECT, EXECUTE ON `nova_cell0`.* TO `accounting-db`@`host.example.com`;
```
                                               |
## Installation

We deploy this with kayobe in our kayobe config repo, but if you want to setup manually you can in two ways

### As a container 

```commandline
docker build . -t harbor.stfc.ac.uk/stfc-cloud/thecount:v1.0.0 -t harbor.stfc.ac.uk/stfc-cloud/thecount:latest
docker run \
    -v thecount.conf:/etc/thecount/thecount.conf \
    -v var/log/thecount/:/var/log/thecount/ \
    harbor.stfc.ac.uk/stfc-cloud/thecount:latest --help
```

on kayobe to get previous data
```
docker run \ 
   --rm \
   -v /opt/kayobe/accounting-service/:/etc/thecount/ \
   --network host harbor.stfc.ac.uk/stfc-cloud/thecount:v1.0.0 \
   --config-path /etc/thecount/thecount.conf \
   --start-time <YYYY-mm-dd> --end-time <YYYY-mm-dd> --all
```


run `--help` for args you can pass in and how they work
see `./thecount.conf.example` for how to create the config file 

### As a package

you can install it as a package too 

```commandline
python -m venv thecount
source thecount/bin/activate
pip install . 
```

then run it as a module

```
python3 -m thecount --help

# run on older pre-defined start and end time (midnight to midnight) 
python -m thecount --config-path /etc/thecount/thecount.conf \
   --start-time 2026-08-27 \
   --end-time 2026-08-28 \
   --interval 1440 \
   --all 

# run using bash date to generate ISO timestamp
python -m thecount --config-path /etc/thecount/thecount.conf \
   --start-time $(date +"%Y-%m-%dT%H:%M:%S" -d "yesterday") \
   --end-time $(date +"%Y-%m-%dT%H:%M:%S") \ 
   --jobs cinder \
   --jobs glance \
   --interval 360 \
   --dry-run \
   --all 

# run continuously starting from older start time (midnight)
python -m thecount --config-path /etc/thecount/thecount.conf --start-time 2026-08-27 --interval 1440 --all 

# run continuously from current time
python -m thecount --config-path /etc/thecount/thecount.conf --interval 1440 --all 

# run only cinder job
python -m thecount --config-path /etc/thecount/thecount.conf --interval 1440 --jobs cinder

# run cinder and manila job
python -m thecount --config-path /etc/thecount/thecount.conf --interval 1440 --jobs cinder --jobs manila

```
