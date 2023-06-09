from typing import List, Dict, Tuple
from openstack.compute.v2.hypervisor import Hypervisor
import openstack
from openstack.compute.v2.aggregate import Aggregate

with openstack.connect("openstack") as conn: #create a connection to openstack
    all_flavors = list(conn.compute.flavors(get_extra_specs=True)) #create a list of all_flavors
    host_typed_flavors = [i for i in all_flavors if "aggregate_instance_extra_specs:hosttype" in i.extra_specs] #create list of flavors with the required tag
    all_aggregates = list(conn.compute.aggregates(get_extra_specs=True)) #create a list of all_aggregates
    host_typed_aggregates: List[Aggregate] = [i for i in all_aggregates if "hosttype" in i.metadata] #create list of all_aggregates with the right tag

smallest_flavors = {} #initiate a list which will contain the smallest flavor for each hosttype
for flavors in host_typed_flavors:
   host_type = flavors["extra_specs"]["aggregate_instance_extra_specs:hosttype"]
   if host_type not in smallest_flavors:
        smallest_flavors[host_type] = flavors
   new_smallest_flavor_size = min(flavors, smallest_flavors[host_type], key=lambda flavors: flavors["ram"])
   smallest_flavors[host_type] = new_smallest_flavor_size

aggregate_smallest_flavor = { #create a dict of the aggregate name to smallest flavor for that aggregate
    aggre_objects["name"]: flavors
    for aggre_objects in host_typed_aggregates
    for flavors in smallest_flavors.values()
    if aggre_objects["metadata"]["hosttype"] == flavors["extra_specs"]["aggregate_instance_extra_specs:hosttype"]
}

for aggregate_name, flavor in aggregate_smallest_flavor.items():
    print(f"The smallest flavor for {aggregate_name} is {flavor.name} which requires {flavor.vcpus} VCPUs and {flavor.ram}mb RAM")


dict_of_hv_names: Dict[Aggregate, List[str]] = {}
for aggres in host_typed_aggregates: #create the dictionary of aggregate: hosts
    aggregate_name = aggres["name"] #equate aggregate_name to the value of each aggregate in host_typed_aggregates
    dict_of_hv_names[aggregate_name] = aggres["hosts"] #assign each aggregate_name as the key to the hosts of each aggregate

# Re-hydrate HV objects
all_hypervisors: List[Hypervisor] = list(conn.compute.hypervisors(details=True))

hv_names: Dict[Aggregate, List[Hypervisor]] = {}
for aggregate, hostnames in dict_of_hv_names.items():
    find_hvs = [i for i in all_hypervisors if i.name in hostnames]
    hv_names[aggregate] = find_hvs

for agg_name, flav in aggregate_smallest_flavor.items():
    hvs = hv_names[agg_name]
    for hv in hvs:
        if (hv.vcpus - hv.vcpus_used - 4) > flav.vcpus and hv.memory_free > flav.ram:
            vm_name = F"aggregates_build_test_from_script_{hv.name}"
            conn.compute.create_server(name=vm_name, image="ubuntu-focal-20.04-nogui", flavor=flav.name, network="Internal", security_groups=[{"name": "default"}], hypervisor_hostname=hv.name)
            print(f"A VM has been created on {hv.name}")


# for aggregate, hvs in hv_names.items():
#     if not hvs:
#         continue
#     largest_memfree_hv = max(hvs, key=lambda x: x.memory_free) #need to pass aggregate_smallest_flavor
#     print(f"Aggregate: {aggregate} has hv: {largest_memfree_hv.name} with memory {largest_memfree_hv.memory_free}mb")

# for aggregate, hv_list in tqdm(dict_of_hv_names.items(), desc="aggregate", leave=False):
#     list_of_hvs_full[aggregate] = get_hv_details(hv_list)

foo = 0

