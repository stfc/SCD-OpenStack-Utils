import os
from typing import List, Dict

import openstack
from openstack.compute.v2.aggregate import Aggregate
from openstack.compute.v2.hypervisor import Hypervisor

os.environ["OS_CLIENT_CONFIG_FILE"] = "clouds.yaml"
conn = openstack.connect("openstack")


def get_image():
    ubuntu_images = conn.image.images(name="ubuntu-focal-20.04-nogui")
    return ubuntu_images


def select_single_image(images):
    for image in images:
        if image.status == "active":
            useable_image = image
    return useable_image


def get_flavors():
    all_flavors = list(conn.compute.flavors(get_extra_specs=True))
    return all_flavors


def find_flavors_with_hosttype():
    host_typed_flavors = [
        i
        for i in get_flavors()
        if "aggregate_instance_extra_specs:hosttype" in i.extra_specs
    ]
    return host_typed_flavors


def get_aggregates():
    all_aggregates = list(conn.compute.aggregates(get_extra_specs=True))
    return all_aggregates


def find_aggregates_with_hosttype():
    host_typed_aggregates: List[Aggregate] = [
        i for i in get_aggregates() if "hosttype" in i.metadata
    ]
    return host_typed_aggregates


def find_smallest_flavors(flavor_list: object) -> object:
    smallest_flavors = {}
    for flavors in flavor_list:
        host_type = flavors["extra_specs"]["aggregate_instance_extra_specs:hosttype"]
        if host_type not in smallest_flavors:
            smallest_flavors[host_type] = flavors
        new_smallest_flavor_size = min(
            flavors, smallest_flavors[host_type], key=lambda flavors: flavors["ram"]
        )
        smallest_flavors[host_type] = new_smallest_flavor_size
    return smallest_flavors


def find_smallest_flavor_for_each_aggregate(flavors_list, aggregate_list):
    aggregate_smallest_flavor = {
        aggre_objects["name"]: flavors
        for aggre_objects in aggregate_list
        for flavors in flavors_list.values()
        if aggre_objects["metadata"]["hosttype"]
        == flavors["extra_specs"]["aggregate_instance_extra_specs:hosttype"]
    }
    return aggregate_smallest_flavor


def create_dictionary_of_aggregates_to_hostnames(aggr_list):
    dict_of_hv_names: Dict[Aggregate, List[str]] = {}
    for aggres in aggr_list:
        aggregate_name = aggres["name"]
        dict_of_hv_names[aggregate_name] = aggres["hosts"]
    return dict_of_hv_names


def list_all_hv_objects():
    all_hypervisors: List[Hypervisor] = list(conn.compute.hypervisors(details=True))
    return all_hypervisors


def create_dict_of_aggregate_to_hv_objects(hv_names_list, full_hv_list):
    hv_names: Dict[Aggregate, List[Hypervisor]] = {}
    for aggregate, hv_hostnames in hv_names_list.items():
        find_hvs = [i for i in full_hv_list if i.name in hv_hostnames]
        hv_names[aggregate] = find_hvs
    return hv_names


def remove_values(dict_of_Agg_to_hvs):
    for key, values in dict_of_Agg_to_hvs.items():
        dict_of_Agg_to_hvs[key] = [obj for obj in values if obj.status == "enabled"]
    return dict_of_Agg_to_hvs


def recontextualise_hvs(aggregate_flavor_list, hv_list):
    dict_of_aggregate_to_hv_objects: Dict[Aggregate, List[Hypervisor]] = {}
    for agg_name, flav in aggregate_flavor_list.items():
        hvs = {agg_name: hv_list[agg_name]}
        dict_of_aggregate_to_hv_objects.update(hvs)
    return dict_of_aggregate_to_hv_objects


def create_vms_on_hvs_with_space(hv_list, aggregate_flavor_list, image):
    created_list = []
    security_group_id = "771352ca-41b7-4fb6-addc-882aa0d1d628"
    network_id = "fa2f5ebe-d0e0-4465-9637-e9461de443f1"
    for agg, hvs in hv_list.items():
        flavor = aggregate_flavor_list[agg]
        if hvs:
            for hv in hvs:
                if (
                    hv.vcpus - hv.vcpus_used - 4
                ) > flavor.vcpus and hv.memory_free > flavor.ram:
                    vm_name = f"aggregates_build_test_from_script_{hv.name}"
                    created_list.append(f"A VM has been created on {hv.name}")
                    os.system(
                        f"openstack server create --image {image.id} --flavor {flavor.id} --security-group {security_group_id} --network {network_id} --hypervisor-hostname {hv.name} --os-cloud openstack --os-compute-api-version 2.79 {vm_name}"
                    )
    return created_list


if __name__ == "__main__":
    flavors_with_hosttype = find_flavors_with_hosttype()
    aggregates_with_hosttype = find_aggregates_with_hosttype()

    smallest_flavors = find_smallest_flavors(flavors_with_hosttype)

    aggregate_to_smallest_flavor_dict = find_smallest_flavor_for_each_aggregate(
        smallest_flavors, aggregates_with_hosttype
    )

    aggregate_to_hostnames_dict = create_dictionary_of_aggregates_to_hostnames(
        aggregates_with_hosttype
    )

    full_hypervisor_object_list = list_all_hv_objects()

    dict_of_aggregates_to_hv_objects = create_dict_of_aggregate_to_hv_objects(
        aggregate_to_hostnames_dict, full_hypervisor_object_list
    )

    dict_of_flavor_to_hypervisor_objects = recontextualise_hvs(
        aggregate_to_smallest_flavor_dict, dict_of_aggregates_to_hv_objects
    )

    new_hv_agg_dict = remove_values(dict_of_flavor_to_hypervisor_objects)

    image = get_image()

    current_image = select_single_image(image)

    print(
        create_vms_on_hvs_with_space(
            dict_of_flavor_to_hypervisor_objects,
            aggregate_to_smallest_flavor_dict,
            current_image,
        )
    )
