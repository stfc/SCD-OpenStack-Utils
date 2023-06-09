# AQ Zombie Finder

## General Info

This is a Python script that when run returns a list of Cloud VMs that no longer exist, and should be investigated to be removed from Aquilon, as well as returning a list of machines using an "-aq" image that aren't being managed by Aquilon.

The script takes ~20 minutes to complete (When run against 280 machines using AQ images) and creates two files, one containing the IPs and Serial numbers of the Aquilon zombie machines and the other containing the IPs of the Openstack machines not being managed by Aquilon.

Unit tests exist which test the logic of the methods the script uses, and the tests should be run whenever changes are made to the code.

Run running the script, enter your FEDID, Password and the IP of the Openstack machine you'll be using.

## Requirements

Script:
paramiko: 2.12.0

Unit tests:
parameterized: 0.9.0

## Setup
Running the script:
'''
$ cd ../aq_zombie_finder
$ pip install -r requirements.txt
$ python3 aq_zombie_finder.py
'''

Running the unit tests:
'''
$ python3 -m unittest test/test_aq_zombie_finder.py
'''