#!/usr/bin/python
import ldap
import ldap.sasl
import json
import sys
import os
from subprocess import Popen, PIPE

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
	# ld = ldap.open("fed.cclrc.ac.uk")
	# ld.protocol_version = ldap.VERSION3
	# user = "CN=<username>,OU=FBU,DC=fed,DC=cclrc,DC=ac,DC=uk"
	# pwd = "<password>"
	# try:
	# 	ld.simple_bind_s(user,pwd)
	# except ldap.LDAPError, e:
	# 	print e
    ld = ldap.initialise("ldap://fed.cclrc.ac.uk")
	auth = ldap.sasl.gssapi("")
	ld.sasl_interactive_bind_s("",auth)

	basedn = "OU=Manual,OU=Distribution Lists,DC=fed,DC=cclrc,DC=ac,DC=uk"

	qurl = ["(|"] + ["(cn="+g+")" for g in groups] + [")"]
	filt = "".join(qurl)
	atrs = ["cn","displayName","member","descripion"]

	results = ld.search(basedn, ldap.SCOPE_SUBTREE, filt, atrs)

	result_set = []
	while 1:
		result_type, result_data = ld.result(results, 0)
		if(result_data == []):
			break
		else:
			if result_type == ldap.RES_SEARCH_ENTRY:
				d = {}
				d["mems"] = ldap_flatusers(result_data[0][1]['member'], ld)
				d["name"] = result_data[0][1]['displayName'][0]
				d["desc"] = d["name"]
				if "description" in result_data:
					d["desc"] = result_data[0][1]['description'][0]
				result_set.append(d)
	ld.unbind_s()
	print result_set
	return result_set

def putter(groups):

	gcmd = "openstack project list -f json --noindent"
	gcj = cl(gcmd)
	gc = json.loads(gcj)
	gs = [c["Name"] for c in gc]

	for g in groups:
		mems = g["mems"]
		name = g["name"]
		desc = g["desc"]

		if name not in gs:
			gacmd = "openstack project create --domain default --description '{0}' '{1}'".format(desc, name)
			cl(gacmd)

		mcmd = "openstack user list --project '{0}' -f json --noindent".format(name)
		mcj = cl(mcmd)

		mc = json.loads(mcj)
		ms = [c["Name"] for c in mc]
		for m in mems:
			if m not in ms:
				macmd = "openstack role add --user '{0}' --user-domain stfc --project '{1}' --project-domain default user".format(m,name)
				cl(macmd)


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Usage: {0} <groups-file>".format(sys.argv[0])
		sys.exit(1)
	else:
		with open(sys.argv[1]) as f:
			fl = f.read().split("\n")[:-1]
			# groupdata = getter(fl)
			# putter(groupdata)
