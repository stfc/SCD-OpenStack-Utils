from openstack import connect


def server_obj_to_len(server_obj) -> int:
    """
    Method that gets the length of a generator object
    :param server_obj: OpenStack generator object from a query
    :return: Integer for the length of the object i.e. number of results
    """
    generator_list = list(server_obj)
    total_results = len(generator_list)
    return total_results


def number_servers_total(conn: connect) -> int:
    """
    Query an OpenStack Cloud to find the total number of instances across
    all projects.
    :param conn: OpenStack cloud connection
    :returns: Number of VMs in total across the cloud
    """
    server_obj = conn.compute.servers(details=False, all_projects=True, limit=10000)
    # get number of items in generator object
    total_instances = server_obj_to_len(server_obj)
    return total_instances


def number_servers_active(conn: connect) -> int:
    """
    Query an OpenStack Cloud to find the number of instances in
    ACTIVE state.
    :param conn: OpenStack Cloud Connection
    :returns: Number of active VMs
    """
    server_obj = conn.compute.servers(
        details=False, all_projects=True, limit=10000, status="ACTIVE"
    )
    # get number of items in generator object
    instance_active = server_obj_to_len(server_obj)
    return instance_active


def number_servers_build(conn: connect) -> int:
    """
    Query an OpenStack Cloud to find the number of instances in
    BUILD state.
    :param conn: OpenStack Cloud Connection
    :returns: Number of VMs in BUILD state
    """
    server_obj = conn.compute.servers(
        details=False, all_projects=True, limit=10000, status="BUILD"
    )
    # get number of items in generator object
    instance_build = server_obj_to_len(server_obj)
    return instance_build


def number_servers_error(conn: connect) -> int:
    """
    Query an OpenStack Cloud to find the number of instances in
    ERROR state.
    :param conn: OpenStack Cloud Connection
    :returns: Number of VMs in ERROR state
    """
    server_obj = conn.compute.servers(
        details=False, all_projects=True, limit=10000, status="ERROR"
    )
    # get number of items in generator object
    instance_err = server_obj_to_len(server_obj)
    return instance_err


def number_servers_shutoff(conn: connect) -> int:
    """
    Query an OpenStack Cloud to find the number of instances in
    SHUTOFF state.
    :param conn: OpenStack Cloud Connection
    :returns: Number of VMs in SHUTOFF (STOPPED) state
    """
    server_obj = conn.compute.servers(
        details=False, all_projects=True, limit=10000, status="SHUTOFF"
    )
    # get number of items in generator object
    instance_shutoff = server_obj_to_len(server_obj)
    return instance_shutoff


def get_all_server_statuses(cloud_name: str, prod: bool) -> str:
    """
    Collects the stats for vms and returns a dict
    :param cloud_name: Name of OpenStack cloud to connect to
    :param prod: Boolean to determine whether Prod or Dev Cloud used
    :return: A comma separated string containing VM states.
    """
    # raise error if cloud connection not given
    if not cloud_name:
        raise ValueError("An OpenStack Connection is required")

    if prod:
        cloud_env = "Prod"
    else:
        cloud_env = "Dev"

    # connect to an OpenStack cloud
    conn = connect(cloud=cloud_name)
    # collect stats in order: total, active, build, error, shutoff
    total_vms = number_servers_total(conn)
    active_vms = number_servers_active(conn)
    build_vms = number_servers_build(conn)
    error_vms = number_servers_error(conn)
    shutoff_vms = number_servers_shutoff(conn)

    server_statuses = f"VMStats,instance={cloud_env}totalVM={total_vms}i,activeVM={active_vms}i,buildVM={build_vms}i,errorVM={error_vms}i,shutoffVM={shutoff_vms}i"

    return server_statuses


if __name__ == "__main__":
    cloud = "openstack"
    print(get_all_server_statuses(cloud, prod=False))
