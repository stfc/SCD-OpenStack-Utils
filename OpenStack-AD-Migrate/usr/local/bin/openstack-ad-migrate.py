#!/usr/bin/python
import ldap
import ldap.sasl
import json
import sys
import os
from subprocess import Popen, PIPE
from ConfigParser import SafeConfigParser

configparser = SafeConfigParser()
try:
        configparser.read('/etc/openstack-utils/config.ini')
        user = configparser.get('ad','userdn')
        pwd = configparser.get('ad','password')
        host = configparser.get('ad','host')
        basedn = configparser.get('ad','basedn')
        domain = configparser.get('openstack','domain')
except:
        print 'Unable to read from config file'
        sys.exit(1)


env = os.environ.copy()

def cl(c):
        p = Popen(c, shell=True, stdout=PIPE, env=env)
        print c
        return p.communicate()[0]

def ldap_flatusers(members, ld):
        ms = []
        for m in members:
                s = m.split(",")
                basedn = ",".join(s[1:])
                filt = s[0]
                props = ["cn","displayName","member"]
                results = ld.search(basedn, ldap.SCOPE_SUBTREE, filt, props)

                while 1:
                        result_type, result_data = ld.result(results, 0)
                        if(result_data == []):
                                break
                        else:
                                if result_type == ldap.RES_SEARCH_ENTRY:
                                        if 'member' in result_data[0][1]:
                                                mems = result_data[0][1]['member']
                                                ms = ms + ldap_flatusers(mems, ld)
                                        else: # is a user
                                                ms.append(result_data[0][1]['cn'][0])
        return ms



def getter(groups):
        ld = ldap.open(host)
        ld.protocol_version = ldap.VERSION3
        try:
                ld.simple_bind_s(user,pwd)
        except ldap.LDAPError, e:
            print e

        qurl = ["(|"] + ["(cn="+g.replace("_20"," ")+")" for g in groups] + [")"]
        filt = "".join(qurl)
        atrs = ["cn","displayName","member","descripion"]

        results = ld.search(basedn, ldap.SCOPE_SUBTREE, filt, atrs)

        result_set = {}
        while 1:
                result_type, result_data = ld.result(results, 0)
                if(result_data == []):
                        break
                else:
                        if result_type == ldap.RES_SEARCH_ENTRY:
                                name = result_data[0][1]['displayName'][0]
                                key = result_data[0][1]['displayName'][0].replace(" ","_20")
                                print name
                                d = {}
                                d["members"] = ldap_flatusers(result_data[0][1]['member'], ld)
                                d["description"] = name
                                d["role"] = groups[key]["role"]
                                if "project" in groups[key].keys():
                                        d["project"] = groups[key]["project"]
                                if "description" in result_data:
                                        d["description"] = result_data[0][1]['description'][0]
                                result_set[name]=d
                                #result_set.append(d)
        ld.unbind_s()

        print result_set
        # for group in groups.keys():
        #       print group
        #       groups[group]["members"] = result_set[group]["mems"]
        # print groups
        return result_set

def putter(groups):

        projectcmd = "openstack project list -f json --noindent"
        projectcj = cl(projectcmd)
        projectc = json.loads(projectcj)
        projectstring = [c["Name"] for c in projectc]

        for g in groups.keys():
                members = groups[g]["members"]
                name = g
                project = name
                if "project" in groups[name].keys():
                        project = groups[g]["project"]
                role = groups[g]["role"]
                description = groups[g]["description"]

                if project not in projectstring:
                        projectcreatecmd = "openstack project create --domain '{0}' --description '{1}' '{2}'".format(domain,description, project)
                        cl(projectcreatecmd)

                projectmembercmd = "openstack user list --project '{0}' -f json --noindent".format(project)
                projectmemberjson = cl(projectmembercmd)

                projectmemberc = json.loads(projectmemberjson)
                projectmemberlist = []
                for projectmember in projectmemberc:
                        print projectmember
                        projectmemberlist.append(projectmember["Name"])
                projectmemberstring = [c["Name"] for c in projectmemberc]
                print "members"
                print members
                print "projectmembers"
                print projectmemberc
                for member in members:
                        if member not in projectmemberlist:
                                macmd = "openstack role add --user '{0}' --user-domain stfc --project '{1}' --project-domain '{2}' '{3}'".format(member,project,domain,role)
                                cl(macmd)


if __name__ == "__main__":
        if len(sys.argv) < 2:
                print "Usage: {0} <groups-file>".format(sys.argv[0])
                sys.exit(1)
        else:
                with open(sys.argv[1]) as f:
                        #fl = f.read().split("\n")[:-1]
                        groupdata = json.load(f)
                        print groupdata
                        groupdata = getter(groupdata)
                        putter(groupdata)
                                                                                                                                                                                   
