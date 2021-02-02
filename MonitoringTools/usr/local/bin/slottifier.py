#!/usr/bin/python
import json
import sys
import os
import requests
from time import gmtime, strftime
from subprocess import Popen, PIPE
from ConfigParser import SafeConfigParser
import math
from time import sleep


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
   print 'Unable to read from config file'
   sys.exit(1)

url = 'http://'+host+'/write?db='+database +'&precision=s'

env = os.environ.copy()

env = os.environ.copy()

# import all variables from the config file
with open('/etc/openstack-utils/slottifier_conf.json') as config_file:
    config = json.load(config_file)

aggregates = config['aggregates']
sourcecmd = config['sourcecmd']

# pass commands to be performed
def command_line(c):
    p = Popen(sourcecmd + c, shell=True, stdout=PIPE, env=env)
    return p.communicate()[0]

flavorListPre = json.loads(command_line("openstack flavor list --long -f json"))
flavorDict = {}
for flavor in flavorListPre:
    flavorDict[flavor["Name"]] = flavor
#print flavorListPre
#print flavorDict

novacomputeservices = json.loads(command_line("openstack compute service list -f json"))

hypervisors = json.loads(command_line("openstack hypervisor list --long -f json"))

slotdict = {}
for flavor in flavorListPre:
    slotdict[flavor["Name"]] = 0

#print slotdict

aggregateGroupsListPre = json.loads(command_line("openstack aggregate list --long -f json"))
aggregateGroupsList = {}
for aggregateGroup in aggregateGroupsListPre:
    totalCoresAvailable = 0
    totalCoresUsed = 0

    aggregateGroupsList[aggregateGroup["Name"]] = aggregateGroup

    aggregateGroupDetails = json.loads(command_line("openstack aggregate show " + aggregateGroup["Name"] + " -f json"))
 #   print aggregateGroup["Name"]
#    if "hosttype" in aggregateGroup["Properties"]:
 #       print aggregateGroup["Properties"]["hosttype"]   
    
    # calculate vcpu's
    uphosts = []
    for host in aggregateGroupDetails["hosts"]:
        for novaservice in novacomputeservices:
            if novaservice["Status"] == "enabled" and novaservice["Host"] == host:
                for hv in hypervisors:
                    if hv["Hypervisor Hostname"] == novaservice["Host"]:
  #                      print hv
                        if hv["vCPUs"] - hv["vCPUs Used"] >= 0:
                            coresAvailable = hv["vCPUs"] - hv["vCPUs Used"]
                        else:
                            coresAvailable = 0
                        if hv["Memory MB"] - hv["Memory MB Used"] >= 0:
                            memAvailable = hv["Memory MB"] - hv["Memory MB Used"]
                        else:
                            memAvailable = 0

                        totalCoresAvailable += hv["vCPUs"]
                        totalCoresUsed += hv["vCPUs Used"]

		        for flavor in flavorListPre:
                           if ("hosttype" in aggregateGroup["Properties"]) and ("aggregate_instance_extra_specs:hosttype" in flavor["Properties"]) and ("aggregate_instance_extra_specs:hosttype='" + aggregateGroup["Properties"]["hosttype"] +"'" in flavor["Properties"]):
   #                            print flavor["Name"]
    #                           print (coresAvailable //flavor["VCPUs"])
                               if (coresAvailable // flavor["VCPUs"]) <= (memAvailable //flavor["RAM"]):
                                   slotdict[flavor["Name"]] += (coresAvailable //flavor["VCPUs"])
                               else:
                                   slotdict[flavor["Name"]] += (memAvailable //flavor["RAM"])
                            	


print slotdict

reportstring = ""
#print limits
for flavor in slotdict:
    #print project
        print flavor
        datastring = ""
        datastring += "SlotsAvailable"
        datastring += ",instance="+instance
        datastring += ",flavor="+flavor
        datastring += " SlotsAvailable=" + str(slotdict[flavor])
        #    else:
         #       if statstring != "":
          #          statstring += ","
           #     statstring += stat + "=" + str(servicedetails[host][service][stat]) +"i"
#        datastring += " " + statstring
        print datastring
        reportstring += datastring
        reportstring += "\n"

print reportstring
r = requests.post(url,data=reportstring,auth=(username,password))
print r.text
print r
