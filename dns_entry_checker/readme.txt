# DNS Entry Checker

## General Info

This is a Python script that when run, create 4 files: one listing IP addresses that don't match their DNS name, one listing the IPs of DNS names that don't go to the correct IP, one listing IPs missing DNS names and one listing the gaps in the IP list.

The script takes ~10 minutes to complete (When run against 4043 IPs)

Unit tests exist which test the logic of the methods the script uses, and the tests should be run whenever changes are made to the code.

Run running the script, enter your FEDID, Password and the IP of the machine you'll be using.

## Requirements

Script:
paramiko: 2.12.0

Unit tests:
parameterized: 0.9.0

## Setup
Running the script:
'''
$ cd ../dns_entry_checker
$ pip install -r requirements.txt
$ python3 dns_entry_checker.py
'''

Running the unit tests:
'''
$ python3 -m unittest discover -s ./test -p "test_*.py"
'''