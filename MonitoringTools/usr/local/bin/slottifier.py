#!/usr/bin/python
from typing import List
import sys
from typing import Dict
import openstack
from slottifier_entry import SlottifierEntry
from send_metric_utils import parse_args, run_scrape

UNKNOWN_GPU_NUM_FLAVORS = []


def get_hv_info(hv_name: str, hypervisors: Dict) -> Dict:
    """
    Helper function to get hv information on cores/memory available
    :param hv_name: hypervisor name to get information from
    :param hypervisors: a list of all hypervisors to search in (avoids long search times by getting each one from openstack)
    :return: a dictionary of cores/memory available for given hv
    """
    hv_info = {"cores_available": 0, "mem_available": 0}
    hypervisor = hypervisors.get(hv_name, {})
    if hypervisor and hypervisor["status"] != "disabled":
        hv_info["cores_available"] = max(0, hypervisor.get("vcpus", 0) - hypervisor.get("vcpus_used", 0))
        hv_info["mem_available"] = max(0, hypervisor.get("memory_size", 0) - hypervisor.get("memory_used", 0))

    return hv_info


def get_flavor_requirements(flavor) -> Dict:
    """
    Helper function to get flavor memory/ram/gpu requirements for a VM of that type to be built on a hv
    :param flavor: flavor to get requirements from
    :return: dictionary of requirements
    """
    return {
        "gpus_required": int(flavor["extra_specs"].get("accounting:gpu_num", 0)),
        "cores_required": int(flavor.get("vcpus", 0)),
        "mem_required": int(flavor.get("ram", 0))
    }


def get_valid_flavors_for_hosttype(flavor_list: List, hypervisor_hosttype: str) -> List:
    """
    Helper function that filters a list of flavors to find those that can be built on a hypervisor with a given hosttype
    :param flavor_list: a list of flavors to check
    :param hypervisor_hosttype: specifies the hypervisor hosttype to find compatible flavors for
    :return: a list of valid flavors for hosttype
    """
    valid_flavors = []
    for flavor in flavor_list:
        # validate that flavor can be used on host aggregate
        if "aggregate_instance_extra_specs:hosttype" not in flavor["extra_specs"].keys():
            continue
        if flavor["extra_specs"]["aggregate_instance_extra_specs:hosttype"] != hypervisor_hosttype:
            continue

        valid_flavors.append(flavor)

    return valid_flavors


def convert_to_data_string(slots_dict: Dict, instance: str) -> str:
    """
    converts a dictionary of values into a data-string influxdb can read
    :param slots_dict: a dictionary of slots available for each flavor
    :param instance: which cloud the info was scraped from (prod or dev)
    :return: a comma-separated string of key=value taken from input dictionary
    """
    data_string = ""
    for flavor, slot_info in slots_dict.items():
        data_string += (
            f"SlotsAvailable,instance={instance},flavor={flavor}"
            f" SlotsAvailable={slot_info.slots_available}"
            f",maxSlotsAvailable={slot_info.max_gpu_slots_capacity}"
            f",usedSlots={slot_info.estimated_gpu_slots_used}"
            f",enabledSlots={slot_info.max_gpu_slots_capacity_enabled}\n"
        )
    return data_string


def calculate_slots_for_flavor_for_hv(flavor_name, flavor_reqs, hv_info) -> SlottifierEntry:
    """
    Helper function that calculates available slots for a flavor on a given hypervisor
    :param flavor_name: name of flavor
    :param flavor_reqs: dictionary of memory, cpu, and gpu requirements of flavor
    :param hv_info: dictionary of memory, cpu, and gpu capacity/availability on hypervisor
        and whether hv compute service is enabled
    :return: A dataclass holding slottifer information to update with
    """
    slots_available = 0
    slots_dataclass = SlottifierEntry()

    if hv_info["compute_service_status"] == "enabled":
        slots_available = min(
            hv_info["cores_available"] // flavor_reqs["cores_required"],
            hv_info["mem_available"] // flavor_reqs["mem_required"]
        )

    if "g-" in flavor_name:

        # workaround for bugs where gpu number not specified
        if flavor_reqs["gpus_required"] == 0:
            flavor_reqs["gpus_required"] = 1
            # For debugging purposes
            if flavor_name not in UNKNOWN_GPU_NUM_FLAVORS:
                UNKNOWN_GPU_NUM_FLAVORS.append(flavor_name)

        # if the number of GPUs currently assigned on this host is 0, this is how many slots are available
        theoretical_gpu_slots_available = hv_info["gpu_capacity"] // flavor_reqs["gpus_required"]

        # estimated number of GPU slots used - based off of how much cpu/mem is currently being used
        slots_dataclass.estimated_gpu_slots_used = hv_info["gpu_capacity"] - slots_available

        slots_dataclass.max_gpu_slots_capacity += hv_info["gpu_capacity"]

        if hv_info["compute_service_status"] == "enabled":
            slots_dataclass.max_gpu_slots_capacity_enabled = hv_info["gpu_capacity"]

        slots_available = min(slots_available, theoretical_gpu_slots_available)

    slots_dataclass.slots_available = slots_available
    return slots_dataclass


def get_slottifier_details(instance: str) -> str:
    """
    This function gets calculates slots available for each flavor in openstack and outputs results in
    data string format which can be posted to InfluxDB
    :param instance: which cloud to calculate slots for
    :return: A data string of scraped info
    """
    conn = openstack.connect(cloud=instance)

    # we get all openstack info first because it is quicker than getting them one at a time
    # dictionaries prevent duplicates
    all_compute_services = {service["id"]: service for service in conn.compute.services()}
    print("got all compute services")
    all_aggregates = {aggregate["id"]: aggregate for aggregate in conn.compute.aggregates()}
    print("got all aggregates")
    all_hypervisors = {h["name"]: h for h in conn.list_hypervisors()}
    print("got all hypervisors")
    all_flavors = {flavor["name"]: flavor for flavor in conn.compute.flavors(get_extra_specs=True)}
    print("got all flavors")

    slots_dict = {flavor_name: SlottifierEntry() for flavor_name in all_flavors}
    for aggregate in all_aggregates.values():

        hv_hosttype = aggregate["metadata"].get("hosttype", None)
        if not hv_hosttype:
            continue

        for compute_service in all_compute_services.values():
            hv_info = get_hv_info(compute_service["host"], all_hypervisors)
            hv_info["gpu_capacity"] = int(aggregate["metadata"].get("gpunum", 0))
            hv_info["compute_service_status"] = compute_service["status"]

            valid_flavors = get_valid_flavors_for_hosttype(list(all_flavors.values()), hv_hosttype)
            for flavor in valid_flavors:
                slots_dict[flavor["name"]] += calculate_slots_for_flavor_for_hv(
                    flavor["name"],
                    get_flavor_requirements(flavor),
                    hv_info,
                )

    return convert_to_data_string(slots_dict, instance)


def main(user_args: List):
    """
    send slottifier info to influx
    :param user_args: args passed into script by user
    """
    influxdb_args = parse_args(user_args, description="Get All Service Statuses")
    run_scrape(influxdb_args, get_slottifier_details)

    # for debugging purposes
    for missing_flavor in UNKNOWN_GPU_NUM_FLAVORS:
        print(
            f"{missing_flavor} missing metadata property 'extra_specs:accounting:gpu_num'"
            "do not know how many GPUs the flavor requires, assuming 1 gpu required"
        )


if __name__ == '__main__':
    main(sys.argv[1:])
