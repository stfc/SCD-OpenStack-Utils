import subprocess, requests, json
from requests_kerberos import HTTPKerberosAuth

#used for finding hostnames based on ip
hostname_url = "http://aquilon.gridpp.rl.ac.uk:6901/find/host?ip={0}"

aq_url_prefix = "https://aquilon.gridpp.rl.ac.uk/private/aqd.cgi"
aq_make = "/host/{0}/command/make"
aq_manage = "/host/{0}/command/manage?hostname={0}&{1}={2}&force=true"
make_reset = "?personality=nubesvms&osversion=6x-x86_64&archetype=ral-tier1&osname=sl"

#using the e-science certificate authority
req_ses = requests.Session()
req_ses.verify = "/etc/grid-security/certificates/"

def fix_json(fake_json):
    """Used after getting json from openstack which returns a list of dictionaries with field, value pairs"""
    if isinstance(fake_json, str): fake_json = json.loads(fake_json)
    out = {}
    for i in fake_json: out[i["Field"]] = i["Value"]
    return out

def attempt_url(url, retry=5):
    """Will attempt a aquilon url command a default of 5 times. Prints instead of returning"""
    auth = HTTPKerberosAuth()
    out = req_ses.post(url, auth=auth).text
    #kerberos authentication goes here
    #if out != "No data" and out != "":
        #subprocess.call(["kinit","-k"])
        #auth = HTTPKerberosAuth()
    print(out)
    count = 0
    while out != "No data" and out != "" and count < retry:
        out = req_ses.post(url, auth=auth).text
        print(out)
        count += 1
    if count < retry: print("VM: - VM Creation - AQ Sandbox/Domain Assigned")
    else: print("VM: - VM Creation - AQ Sandbox/Domain Failed")

def get_address_dict(addresses):
    """Converts the addresses field from openstack output into a dictionary of lists per address type"""
    if not "=" in addresses: return {}
    addresses = addresses.replace(" ","")
    addresses = addresses.split(";")
    d = {}
    for i in addresses:
        i = i.split("=")
        d[i[0]] = i[1].split(",")
    return d

def get_hostname(payload):
    """Returns a "hostname" based on payload information"""
    if isinstance(payload, str): payload = json.loads(payload)
    if payload.get("fixed_ips"):
        ips = payload["fixed_ips"]
        for i in ips:
            if i["label"] == "public":
                ip = i["address"]
                hostname = req_ses.get(hostname_url.format(ip)).text
                if hostname:
                    return hostname
    if payload.get("instance_id"):
        iid = payload["instance_id"]
        vm_info = subprocess.Popen(["openstack","server","show",iid,"-fjson"], stdout=subprocess.PIPE).communicate()[0]
        if vm_info == "":
            return None
        vm_info = fix_json(vm_info)
        addresses = get_address_dict(vm_info["addresses"])
        if addresses.get("public"):
            ip = addresses["public"][0]
            hostname = req_ses.get(hostname_url.format(ip)).text
            if hostname:
                return hostname
    #this is if all else fails. this hostname wont work when trying an aquilon command
    if payload.get("hostname"):
        return payload["hostname"]
    else:
        return None

def vm_delete(payload):
    hostname = get_hostname(payload)
    if hostname == None:
        print("Hostname can't be found")
        return
    aq_url = aq_url_prefix + aq_manage.format(hostname, "domain", "prod")
    print(aq_url)
    attempt_url(aq_url)
    aq_url = aq_url_prefix + aq_make.format(hostname) + make_reset
    print(aq_url)
    attempt_url(aq_url)


def vm_create(payload):
    if payload["metadata"]:
        metadata = payload["metadata"]
        hostname = get_hostname(payload)
        if hostname == None:
            print("Hostname can't be found")
            return

        if metadata.get("AQ_SANDBOX") or metadata.get("AQ_DOMAIN"):
            if metadata.get("AQ_SANDBOX"):
                aq_url = aq_url_prefix + aq_manage.format(hostname, "sandbox", metadata["AQ_SANDBOX"])
            else:
                aq_url = aq_url_prefix + aq_manage.format(hostname, "domain", metadata["AQ_DOMAIN"])
            print(aq_url)
            attempt_url(aq_url)

        make_suffix = []
        if metadata.get("AQ_ARCHETYPE"):
            make_suffix.append("archetype=" + metadata["AQ_ARCHETYPE"])
        if metadata.get("AQ_PERSONALITY"):
            make_suffix.append("personality=" + metadata["AQ_PERSONALITY"])
        if metadata.get("AQ_OS"):
            make_suffix.append("osname=" + metadata["AQ_OS"])
        if metadata.get("AQ_OSVERSION"):
            make_suffix.append("osversion=" + metadata["AQ_OSVERSION"])
        if make_suffix:
            make_url_suffix = "?" + "&".join(make_suffix)
            aq_url = aq_url_prefix + aq_make.format(hostname) + make_url_suffix
            print(aq_url)
            attempt_url(aq_url)
    else:
        print("No metadata, skipping")
