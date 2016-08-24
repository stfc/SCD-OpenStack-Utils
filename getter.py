#!/usr/bin/python
import ldap
import json
import sys

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
						ms = ms + ldap_flatusers(mems)
					else: # is a user
						ms.append(m)
	return ms				
		
		

def getter(groups):
	ld = ldap.open("fed.cclrc.ac.uk")
	ld.protocol_version = ldap.VERSION3
	user = "CN=huq39111,OU=FBU,DC=fed,DC=cclrc,DC=ac,DC=uk"
	pwd = "mq<2xb>aw8"
	try:
		ld.simple_bind_s(user,pwd)
	except ldap.LDAPError, e:
		print e


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
	return result_set

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Usage: {0} <groups-file>".format(sys.argv[0])
		sys.exit(1)
	else:
		with open(sys.argv[1]) as f:
			fl = f.read().split("\n")[:-1]
			groupdata = getter(fl)
			print groupdata
