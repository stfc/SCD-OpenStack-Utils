#!/usr/bin/python
import json
import sys
import os
import requests
from subprocess import Popen, PIPE
from ConfigParser import SafeConfigParser

env = os.environ.copy()

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

sourcecmd = "source /etc/openstack-utils/admin-openrc.sh;"

def cl(c):
        p = Popen(sourcecmd+c, shell=True, stdout=PIPE, env=env)
#        print c
        return p.communicate()[0]


projectcmd = "openstack project list -f json --noindent"
projectlistjson = cl(projectcmd)
projectlist = json.loads(projectlistjson)

limits = {}
#project = projectlist[0]
for project in projectlist:
    if "_rally" not in project and "844" not in project:
    #print project["ID"]
    #print project["Name"]
        projectlimitscmd = "openstack limits show -f json --noindent --absolute --project " + project["ID"]
        try:
            projectlimitsjson = cl(projectlimitscmd)
            projectlimits = json.loads(projectlimitsjson)
            limits[project["Name"]] = projectlimits
        except ValueError:
            print project["Name"] + " does not exist"

reportstring = ""
#print limits
for project in limits:
    #print project
    if "_rally" not in project:
        datastring = ""
        datastring += "Limits"
        datastring += ",Project=\"" + project.replace(' ','\ ') + "\""
        datastring += ",instance="+instance
        limitstring = ""
        for limit in limits[project]:
            #print limit
            #print limit["Name"]
            #print " " + limit["Name"] + "=" + str(limit["Value"])
            if limitstring != "":
                limitstring += ","
            limitstring += limit["Name"] + "=" + str(limit["Value"]) +"i"
        datastring += " " + limitstring
        print datastring 

        reportstring += datastring
        reportstring += "\n"

r = requests.post(url,data=reportstring,auth=(username,password))
print r.text
print r
