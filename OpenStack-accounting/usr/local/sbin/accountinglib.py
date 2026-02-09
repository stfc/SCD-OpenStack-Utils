#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
import time
import datetime

# from datetime import datetime,time
import json
import requests
import sys
import sqlalchemy
import logging
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
import configparser


def get_logger(component):
    logging.basicConfig(
        filename="/var/log/thecount.log",
        format=f"%(asctime)s {component} %(message)s",
        filemode="a",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def ifnull(var, val):
    """Returns the second argument if the first argument is Null/None"""
    if var is None:
        return val
    return var


def project_to_department(result):
    """Returns an appropriate department for a project"""
    if "rally" in result["Project"]:
        department = "STFC Cloud"
    elif "efault" in result["Department"]:
        department = result["Project"]
    else:
        department = result["Department"]
    return department


def send_to_influx(datastring, logger):
    """Takes a datastring formatted to send to InfluxDBs rest api. Loads necessary config, sends and returns the response"""
    # Read from config file
    influx_parser = configparser.SafeConfigParser()
    try:
        influx_parser.read("/etc/influxdb.conf")
    except Exceptions as exp:
        logger.info(f"Unable to read from influx config file - {str(exp)}")
        sys.exit(1)
    try:
        host = influx_parser.get("db", "host")
        database = influx_parser.get("db", "database")
        username = influx_parser.get("auth", "username")
        password = influx_parser.get("auth", "password")
        instance = influx_parser.get("cloud", "instance")
    except Exceptions as exp:
        logger.info(f"Unable to parse influx config file - {str(exp)}")
        sys.exit(1)
    finaldatastring = datastring.replace(
        "Accounting,", "Accounting,instance=" + instance + ","
    )
    logger.info(finaldatastring)
    url = f"http://{host}/write?db={database}&precision=s"
    response = requests.post(url, data=finaldatastring, auth=(username, password))
    return response


def get_accounting_data(database, starttime, endtime, logger):
    """Takes a db name and a start and end time as arguments. Loads db config, creates a db connection and runs a stored procedure. Returns the results of the stored procedure"""
    thecount_parser = configparser.RawConfigParser(strict=False)

    try:
        thecount_parser.read("/etc/thecount/thecount.conf")
    except Exceptions as exp:
        logger.info(f"Unable to read from thecount config file - {str(exp)}")
        sys.exit(1)

    try:
        connectionstring = (
            thecount_parser.get("database", "connection") + "/" + database
        )
    except Exceptions as exp:
        logger.info(f"Unable to parse thecount config file - {str(exp)}")
        sys.exit(1)

    engine = sqlalchemy.create_engine(connectionstring, encoding="utf-8")
    connection = engine.connect()
    sess = sessionmaker(bind=engine)()
    query = f'call get_accounting_data( "{starttime}","{endtime}")'

    logger.info(query)
    results = sess.execute(query, {"p1": starttime, "p2": endtime})
    return results
