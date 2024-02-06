import openstack


def number_servers_total(conn):
    """
    Query an OpenStack Cloud to find the total number of instances across
    all projects.
    :param conn: OpenStack cloud connection
    :returns: Number of VMs in total across the cloud
    """
    # all_projects set to false while testing methods against one project
    server_obj = conn.compute.servers(details=False, all_projects=False)
    # get number of items in generator object
    instance_list = list(server_obj)
    total_instances = len(instance_list)
    return total_instances


def number_servers_active(conn):
    """
    Query an OpenStack Cloud to find the number of instances in
    ACTIVE state.
    :param conn: OpenStack Cloud Connection
    :returns: Number of active VMs
    """
    # all_projects set to false while testing methods against one project
    server_obj = conn.compute.servers(
        details=False, all_projects=False, status="ACTIVE"
    )
    # get number of items in generator object
    instance_list = list(server_obj)
    instance_active = len(instance_list)
    return instance_active


def number_servers_build(conn):
    """
    Query an OpenStack Cloud to find the number of instances in
    BUILD state.
    :param conn: OpenStack Cloud Connection
    :returns: Number of VMs in BUILD state
    """
    # all_projects set to false while testing methods against one project
    server_obj = conn.compute.servers(details=False, all_projects=False, status="BUILD")
    # get number of items in generator object
    instance_list = list(server_obj)
    instance_build = len(instance_list)
    return instance_build


def number_servers_error(conn):
    """
    Query an OpenStack Cloud to find the number of instances in
    ERROR state.
    :param conn: OpenStack Cloud Connection
    :returns: Number of VMs in ERROR state
    """
    # all_projects set to false while testing methods against one project
    server_obj = conn.compute.servers(details=False, all_projects=False, status="ERROR")
    # get number of items in generator object
    # get number of items in generator object
    instance_list = list(server_obj)
    instance_err = len(instance_list)
    return instance_err


def number_servers_shutoff(conn):
    """
    Query an OpenStack Cloud to find the number of instances in
    SHUTOFF state.
    :param conn: OpenStack Cloud Connection
    :returns: Number of VMs in SHUTOFF (STOPPED) state
    """
    # all_projects set to false while testing methods against one project
    server_obj = conn.compute.servers(
        details=False, all_projects=False, status="SHUTOFF"
    )
    # get number of items in generator object
    instance_list = list(server_obj)
    instance_shutoff = len(instance_list)
    return instance_shutoff


def collect_stats(cloud, prod):
    """
    Collects the stats for vms and returns a dict
    :param cloud: OpenStack Cloud connection
    :param prod: Boolean to determine whether Prod or Dev Cloud used
    :return: A comma separated string containing VM states.
    """
    # raise error if cloud connection not given
    if not cloud:
        raise ValueError("An OpenStack Connection is required")

    # collect stats in order: total, active, build, error, shutoff
    total_vms = number_servers_total(cloud)
    active_vms = number_servers_active(cloud)
    build_vms = number_servers_build(cloud)
    error_vms = number_servers_error(cloud)
    shutoff_vms = number_servers_shutoff(cloud)

    if prod:
        cloud_env = "Prod"
    else:
        cloud_env = "PreProd"

    vm_stats = f"VMStats, instance={cloud_env} totalVM={total_vms}i,activeVM={active_vms}i,buildVM={build_vms}i,errorVM={error_vms}i,shutoffVM={shutoff_vms}i"

    return vm_stats


if __name__ == "__main__":
    cloud_conn = openstack.connect(cloud="openstack")
    print(collect_stats(cloud_conn, prod=False))
