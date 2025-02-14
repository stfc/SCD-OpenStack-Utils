import yaml
from pprint import pprint

import datetime

with open("compute_service.yaml", "r", encoding="utf-8") as file:
    compute_service = yaml.safe_load(file)

with open("hypervisor.yaml", "r", encoding="utf-8") as file:
    hypervisor = yaml.safe_load(file)

with open("fip.yaml", "r", encoding="utf-8") as file:
    fip = yaml.safe_load(file)

with open("server.yaml", "r", encoding="utf-8") as file:
    server = yaml.safe_load(file)


hvs_enabled = [hv for hv in compute_service if hv["Status"] == "enabled"]
hvs_up = len([hv for hv in hvs_enabled if hv["State"] == "up"])
hvs_down = len([hv for hv in hvs_enabled if hv["State"] == "down"])
hvs_disabled = len([hv for hv in hvs_enabled if hv["State"] == "up" and hv["Status"] == "disabled"])

memory_used = round(sum([hv["Memory MB Used"] for hv in hypervisor if hv["State"] == "up"])/1000000, 2)
memory_total = round(sum([hv["Memory MB"] for hv in hypervisor if hv["State"] == "up"])/1000000, 2)

cpu_used = sum([hv["vCPUs Used"] for hv in hypervisor if hv["State"] == "up"])
cpu_total = sum([hv["vCPUs"] for hv in hypervisor if hv["State"] == "up"])

hvs_up_and_cpu_full = len([hv for hv in hypervisor if hv["vCPUs Used"] == hv["vCPUs"] and hv["State"] == "up"])
hvs_up_and_memory_full = len([hv for hv in hypervisor if (hv["Memory MB"]-hv["Memory MB Used"] <= 8192 and hv["State"] == "up")])

fip_total = fip["used_ips"]
fip_used = fip["total_ips"]

vm_active = len([vm for vm in server if vm["Status"] == "ACTIVE"])
vm_error = len([vm for vm in server if vm["Status"] == "ERROR"])
vm_build = len([vm for vm in server if vm["Status"] == "BUILD"])
vm_shutoff = len([vm for vm in server if vm["Status"] == "SHUTOFF"])



data = {}
data["memory"] = {"in_use": memory_used, "total": memory_total}
data["cpu"] = {"in_use": cpu_used, "total": cpu_total}
data["hv"] = {"active": {"active": hvs_up, "cpu_full": hvs_up_and_cpu_full, "memory_ful": hvs_up_and_memory_full}, "down": hvs_down, "disabled": hvs_disabled}
data["floating_ip"] = {"in_use": fip_used, "total": fip_total}
data["vm"] = {"active": vm_active, "shutoff": vm_shutoff, "errored": vm_error, "building": vm_build}

with open(f"data-{datetime.datetime.now().isocalendar().week}.yaml", "w", encoding="utf-8") as file:
    yaml.dump(data, file)



