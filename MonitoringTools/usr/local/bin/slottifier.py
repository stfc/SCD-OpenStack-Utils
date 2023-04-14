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

novacomputeservices = json.loads(command_line("openstack compute service list -f json"))

hypervisors = json.loads(command_line("openstack hypervisor list --long -f json"))

slotdict = {}
for flavor in flavorListPre:
    slotdict[flavor["Name"]] = 0

aggregateGroupsListPre = json.loads(command_line("openstack aggregate list --long -f json"))
aggregateGroupsList = {}
for aggregateGroup in aggregateGroupsListPre:
    totalCoresAvailable = 0
    totalCoresUsed = 0

    aggregateGroupsList[aggregateGroup["Name"]] = aggregateGroup

    aggregateGroupDetails = json.loads(command_line("openstack aggregate show " + aggregateGroup["Name"] + " -f json"))

    # calculate vcpu's
    uphosts = []
    for host in aggregateGroupDetails["hosts"]:
        for novaservice in novacomputeservices:
            if novaservice["Status"] == "enabled" and novaservice["Host"] == host:
                for hv in hypervisors:
                    if hv["Hypervisor Hostname"] == novaservice["Host"]:
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
                               if ("local-storage-type" in flavor["Properties"]) :
                                   if ("local-storage-type" in aggregateGroup["Properties"]) and ("local-storage-type='" + aggregateGroup["Properties"]["local-storage-type"] +"'" in flavor["Properties"]):
                                       if (coresAvailable // flavor["VCPUs"]) <= (memAvailable //flavor["RAM"]):
                                            slotsAvailable = (coresAvailable //flavor["VCPUs"])
                                       else:
                                            slotsAvailable= (memAvailable //flavor["RAM"])

                               else:
                                   if (coresAvailable // flavor["VCPUs"]) <= (memAvailable //flavor["RAM"]):
                                       slotsAvailable = (coresAvailable //flavor["VCPUs"])
                                   else:
                                       slotsAvailable= (memAvailable //flavor["RAM"])
                               if "g-" in flavor["Name"] :
                                   slotsByCPU = hv["vCPUs"] // flavor["VCPUs"] # can the hv hold any of this flavor, how many
                                   hostGPUNum = int(aggregateGroup["Properties"]["gpunum"]) # how many gpus are in an a host in this aggregate
                                   flavorProperties = flavor["Properties"] # extract the metadata for the flavor
                                   for flavorProperty in flavorProperties.split(", "):
                                       if "accounting:gpu_num" in flavorProperty:
                                           flavorGPUNum = int(flavorProperty.replace("accounting:gpu_num='","").replace("'","")) # break the metadata down to the bit we need
                                   coresAvailable = hv["vCPUs"] - hv["vCPUs Used"] # how many cpu cores are available on the host
                                   theoreticalSlots = hostGPUNum // flavorGPUNum # if the hv is empty how many instances of the flavor fit
                                   gpuSlotsAvailable = coresAvailable // flavor["VCPUs"] # how many of the flavors would fit into the available cpus
                                   if (gpuSlotsAvailable > theoreticalSlots):
                                       slotsAvailable = theoreticalSlots
                                   else:
                                       slotsAvailable = gpuSlotsAvailable

                               slotdict[flavor["Name"]] += slotsAvailable



print(slotdict)

reportstring = ""
for flavor in slotdict:
        print flavor
        datastring = ""
        datastring += "SlotsAvailable"
        datastring += ",instance="+instance
        datastring += ",flavor="+flavor
        datastring += " SlotsAvailable=" + str(slotdict[flavor])
        reportstring += datastring
        reportstring += "\n"

r = requests.post(url,data=reportstring,auth=(username,password))
print(r.text)
print(r)
