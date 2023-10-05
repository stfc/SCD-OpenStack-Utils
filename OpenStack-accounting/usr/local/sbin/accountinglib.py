#!/usr/bin/python3
import time
import datetime
#from datetime import datetime,time
import json
import requests
import sys
import sqlalchemy
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
import configparser

def ifnull(var, val):
    ```Returns the second argument if the first argument is Null/None```
    if var is None:
        return val
    return var

def send_to_influx(datastring):
    ```Takes a datastring formatted to send to InfluxDBs rest api. Loads necessary config, sends and returns the response```
     # Read from config file
     influx_parser = configparser.SafeConfigParser()
     try:
         influx_parser.read('/etc/influxdb.conf')
         host = influx_parser.get('db', 'host')
         database = influx_parser.get('db', 'database')
         username = influx_parser.get('auth', 'username')
         password = influx_parser.get('auth', 'password')
         instance = influx_parser.get('cloud','instance')
     except:
         print('Unable to read from influx config file')
         sys.exit(1)
     finaldatastring = datastring.replace("Accounting,","Accounting,instance="+instance+",")
     print(finaldatastring)
     url = 'http://'+host+'/write?db='+database +'&precision=s'
     response = requests.post(url,data=finaldatastring,auth=(username,password))
     return response

def get_accounting_data(database,starttime,endtime):
    ```Takes a db name and a start and end time as arguments. Loads db config, creates a db connection and runs a stored procedure. Returns the results of the stored procedure```
    thecount_parser = configparser.RawConfigParser(strict=False)

    try:
        thecount_parser.read('/etc/thecount/thecount.conf')
        connectionstring = thecount_parser.get('database','connection') + '/' + database
    except:
        print('Unable to read from thecount config file')
        sys.exit(1)

    engine = sqlalchemy.create_engine(connectionstring, encoding='utf-8')
    connection = engine.connect()
    sess = sessionmaker(bind=engine)()
    query = 'call get_accounting_data( "' + starttime +'","' + endtime + '")'

    print(query)
    results = sess.execute(query, { 'p1': starttime, 'p2': endtime })
    return results
