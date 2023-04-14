#!/usr/bin/python
import time
import datetime
#from datetime import datetime,time
import json
import requests
import sys
import sqlalchemy
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from ConfigParser import SafeConfigParser

#This config parsing needs rewriting to support python3
#The parsing of the nova.conf seems to not work with the python3 version

# Read from config file
parser = SafeConfigParser()
try:
   parser.read('/etc/influxdb.conf')
   host = parser.get('db', 'host')
   database = parser.get('db', 'database')
   username = parser.get('auth', 'username')
   password = parser.get('auth', 'password')
   instance = parser.get('cloud','instance')
except:
   raise RuntimeError('Unable to read from config file')
   sys.exit(1)

url = 'http://'+host+'/write?db='+database +'&precision=s'

nowtime = time.localtime()

try:
   parser.read('/etc/nova/nova.conf')
   connectionstring = parser.get('database','connection')
except:
   raise RuntimeError('Unable to read from config file')
   sys.exit(1)

starttime=sys.argv[1]
print(starttime)
endtime=sys.argv[2]
print(endtime)
endyyyymm=datetime.datetime.strptime(endtime,"%Y-%m-%d %H:%M").strftime('%Y-%m')
endtimestamp = time.mktime(datetime.datetime.strptime(endtime, "%Y-%m-%d %H:%M").timetuple())
print(endtimestamp)

engine = sqlalchemy.create_engine(connectionstring, encoding='utf-8')
connection = engine.connect()
sess = sessionmaker(bind=engine)()
query = 'call get_accounting_data( "' + starttime +'","' + endtime + '")'


print(query)
results = sess.execute(query, { 'p1': starttime, 'p2': endtime })


datastring = ''
for result in results:
    print(result)

    try:
        if "rally" in result["Project"] :
            department="STFC Cloud"
        else:
            if "default" in result["Department"]:
                department=result["Project"]
            else:
                department=result["Department"]

    except:
        department="UNKNOWN"

    instancetype=result['Charge_Unit']


    datastring += "Accounting"
    datastring += ",instance="+instance
    datastring += ",AvailabilityZone="+result["AvailabilityZone"]
    datastring += ",Project="+result["Project"].replace(' ','\ ')
    datastring += ",Department="+department.replace(' ','\ ')
    datastring += ",Flavor="+result["Flavor"].replace('.','_')
    datastring += ",FlavorPrefix="+result["Flavor"].split('.')[0]
    datastring += ",InstanceType="+instancetype
    datastring += ",YYYY-MM="+ endyyyymm
    datastring += ",Charge_Unit="+ result["Charge_Unit"]
    datastring += " VMs="+str(result["VMs"])
    datastring += ",VM_Seconds="+str(result["VM_Seconds"])
    datastring += ",Memory_MB_Seconds="+str(result["Memory_MB"] * result['VM_Seconds'])
    datastring += ",Memory_MBs="+str(result["Memory_MB"] * result["VMs"])
    datastring += ",VCPU_Seconds="+str(result["VCPU"] * result['VM_Seconds'])
    datastring += ",VCPUs="+str(result["VCPU"] * result["VMs"])
    datastring += ",Swap_Seconds="+str(result["Swap"] * result['VM_Seconds'])
    datastring += ",Swaps="+str(result["Swap"] * result["VMs"])
    datastring += ",Root_GB_Seconds="+str(result["Root_GB"] * result['VM_Seconds'])
    datastring += ",Root_GBs="+str(result["Root_GB"] * result["VMs"])
    datastring += ",Ephemeral_GB_Seconds="+str(result["Ephemeral_GB"]  * result['VM_Seconds'])
    datastring += ",Ephemeral_GBs="+str(result["Ephemeral_GB"] * result["VMs"])
    if result["GPU_Num"] > 0:
        datastring += ",GPU_Seconds="+str(float(result["GPU_Num"]) * float(result['VM_Seconds']))
        datastring += ",GPUs=" + str(float(result["GPU_Num"]) * float(result['VMs']))
        print(result)
        datastring += ",COST=" + str(float(result["GPU_Num"]) * float(result['VM_Seconds']) * float(result["Per_Unit_Cost"]) / float(3600))
    else:
        datastring += ",COST=" + str(float(result["VCPU"]) * float(result['VM_Seconds']) * float(result["Per_Unit_Cost"]) / float(3600))
        datastring += ",GPUs=" + str(0)
        datastring += ",GPU_Seconds=" + str(0)

    datastring += " "+str(long(endtimestamp))
    datastring += "\n"

print(datastring)


r = requests.post(url,data=datastring,auth=(username,password))
print(r.text)
print(r)
