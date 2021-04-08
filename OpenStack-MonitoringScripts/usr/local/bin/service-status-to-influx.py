#!/usr/bin/python
import json
import sys
import os
import requests
from subprocess import Popen, PIPE
from ConfigParser import SafeConfigParser

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

sourcecmd = "source /etc/openstack-utils/admin-openrc.sh;"

def cl(c):
        p = Popen(sourcecmd+c, shell=True, stdout=PIPE, env=env)
#        print c
        return p.communicate()[0]

#get list of host aggregates
aggregatelist =  json.loads(cl("openstack aggregate list -f json"))



#get hypervisor details
hypervisordetails = json.loads(cl("openstack hypervisor list --long -f json"))

computeservicestatus = json.loads(cl("openstack compute service list -f json"))

neutronservicestatus = json.loads(cl("openstack network agent list -f json"))

#volumeservicestatus = json.loads(cl("openstack volume service list -f json"))

servicedetails = {}
aggregatemapping = {}
for aggregate in aggregatelist:
    aggregatehosts = json.loads(cl("openstack aggregate show -f json \"" + aggregate["Name"] + "\""))
    for host in aggregatehosts["hosts"]:
        aggregatemapping[host] = aggregate

for hv in hypervisordetails:
    if hv["Hypervisor Hostname"] not in servicedetails:
        servicedetails[hv["Hypervisor Hostname"]] = {}
    servicedetails[hv["Hypervisor Hostname"]]["hv"] = {}
    if hv["Hypervisor Hostname"] in aggregatemapping:
        servicedetails[hv["Hypervisor Hostname"]]["hv"]["aggregate"] = aggregatemapping[hv["Hypervisor Hostname"]]["Name"]
    else:
        servicedetails[hv["Hypervisor Hostname"]]["hv"]["aggregate"] = "no-aggregate"
    servicedetails[hv["Hypervisor Hostname"]]["hv"]["memorymax"] = hv["Memory MB"]
    servicedetails[hv["Hypervisor Hostname"]]["hv"]["memoryused"] = hv["Memory MB Used"]
    servicedetails[hv["Hypervisor Hostname"]]["hv"]["memoryavailable"] = hv["Memory MB"] - hv["Memory MB Used"]
    servicedetails[hv["Hypervisor Hostname"]]["hv"]["cpumax"] = hv["vCPUs"]
    servicedetails[hv["Hypervisor Hostname"]]["hv"]["cpuused"] = hv["vCPUs Used"]
    servicedetails[hv["Hypervisor Hostname"]]["hv"]["cpuavailable"] = hv["vCPUs"] - hv["vCPUs Used"]
    servicedetails[hv["Hypervisor Hostname"]]["hv"]["agent"] = 1
    if hv["State"] == "up":
       servicedetails[hv["Hypervisor Hostname"]]["hv"]["state"] = 1
       servicedetails[hv["Hypervisor Hostname"]]["hv"]["statetext"] = "Up"
    else:
       servicedetails[hv["Hypervisor Hostname"]]["hv"]["state"] = 0
       servicedetails[hv["Hypervisor Hostname"]]["hv"]["statetext"] = "Down"

#print servicedetails["hv103.nubes.rl.ac.uk"]

for computeservice in computeservicestatus:
    if computeservice["Host"] not in servicedetails:
        servicedetails[computeservice["Host"]] = {}
    servicedetails[computeservice["Host"]][computeservice["Binary"]] = {}
    servicedetails[computeservice["Host"]][computeservice["Binary"]]["agent"] = 1
    if computeservice["Status"] == "enabled":
        servicedetails[computeservice["Host"]][computeservice["Binary"]]["status"] = 1
        servicedetails[computeservice["Host"]][computeservice["Binary"]]["statustext"] = "Enabled"
        print computeservice["Host"]
        if computeservice["Binary"] == "nova-compute" and "hv" in servicedetails[computeservice["Host"]].keys():
            servicedetails[computeservice["Host"]]["hv"]["status"] = 1
            servicedetails[computeservice["Host"]]["hv"]["statustext"] = "Enabled"
    else:
        servicedetails[computeservice["Host"]][computeservice["Binary"]]["status"] = 0
        servicedetails[computeservice["Host"]][computeservice["Binary"]]["statustext"] = "Disabled"
        if computeservice["Binary"] == "nova-compute" and "hv" in servicedetails[computeservice["Host"]].keys():
            servicedetails[computeservice["Host"]]["hv"]["status"] = 0
            servicedetails[computeservice["Host"]]["hv"]["statustext"] = "Disabled"
    if computeservice["State"] == "up":
        servicedetails[computeservice["Host"]][computeservice["Binary"]]["state"] = 1
        servicedetails[computeservice["Host"]][computeservice["Binary"]]["statetext"] = "Up"
    else:
        servicedetails[computeservice["Host"]][computeservice["Binary"]]["state"] = 0
        servicedetails[computeservice["Host"]][computeservice["Binary"]]["statetext"] = "Down"

for neutronservice in neutronservicestatus:
    if neutronservice["Host"] not in servicedetails:
        servicedetails[neutronservice["Host"]] = {}
    servicedetails[neutronservice["Host"]][neutronservice["Binary"]] = {}
    servicedetails[neutronservice["Host"]][neutronservice["Binary"]]["agent"] = 1
    if neutronservice["Alive"] == ":-)":
        servicedetails[neutronservice["Host"]][neutronservice["Binary"]]["state"] = 1
        servicedetails[neutronservice["Host"]][neutronservice["Binary"]]["statetext"] = "Up"
    else:
        servicedetails[neutronservice["Host"]][neutronservice["Binary"]]["state"] = 0
        servicedetails[neutronservice["Host"]][neutronservice["Binary"]]["statetext"] = "Down"
    if neutronservice["State"] == "UP":
        servicedetails[neutronservice["Host"]][neutronservice["Binary"]]["status"] = 1
        servicedetails[neutronservice["Host"]][neutronservice["Binary"]]["statustext"] = "Enabled"
    else:
        servicedetails[neutronservice["Host"]][neutronservice["Binary"]]["status"] = 0
        servicedetails[neutronservice["Host"]][neutronservice["Binary"]]["statustext"] = "Disabled"

    
#print servicedetails

    

#limits = {}
#project = projectlist[0]
#for project in projectlist:
    #print project["ID"]
    #print project["Name"]
#    projectlimitscmd = "openstack limits show -f json --noindent --absolute --project " + project["ID"]
#    try:
#        projectlimitsjson = cl(projectlimitscmd)
#        projectlimits = json.loads(projectlimitsjson)
#        limits[project["Name"]] = projectlimits
#    except ValueError:
#        print project["Name"] + " does not exist"

reportstring = ""
#print limits
for host in servicedetails:
    for service in servicedetails[host]:
    #print project
        datastring = ""
        datastring += "ServiceStatus"
        datastring += ",host=\"" + host + "\""
        datastring += ",service=\"" + service + "\""
        datastring += ",instance="+instance
        statstring = ""
        for stat in servicedetails[host][service]:
            statdatastring = datastring
            #print limit
            #print limit["Name"]
            #print " " + limit["Name"] + "=" + str(limit["Value"])
            if stat == "statetext" or stat == "statustext" or stat == "aggregate":
                
                datastring += "," + stat + "=\"" + str(servicedetails[host][service][stat]) + "\"" 
            else:
                if statstring != "":
                    statstring += ","
                statstring += stat + "=" + str(servicedetails[host][service][stat]) +"i"
        datastring += " " + statstring
        print datastring 
        reportstring += datastring
        reportstring += "\n"

r = requests.post(url,data=reportstring,auth=(username,password))
print r.text
print r
