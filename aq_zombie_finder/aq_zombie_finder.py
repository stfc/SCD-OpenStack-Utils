from re import compile as re_compile
from pathlib import Path
import argparse
import os
import sys
import paramiko


def create_client(host, user, password):
    """
    Function to create an SSH client through Paramiko
        :param host: hostname to connect to (string)
        :param user: user to connect as (string)
        :param password: password for the user (string)
        :returns:  Configured Paramiko SSHClient object
    """
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(hostname=host, username=user, password=password, timeout=60)
    return client


def ssh_command(client, command):
    """
    Function to execute a command over an SSH client through Paramiko
        :param client: Paramiko client (client)
        :param command: user to connect as (string)
        :returns:  Console output of the command
    """
    _, _stdout, _ = client.exec_command(command, get_pty=True, timeout=60)
    _stdout.channel.recv_exit_status()
    return _stdout.readlines()


def get_aq_ips(openstack_client):
    """
    Function to run a command on the openstack VM
        :param openstack_client: Paramiko client (client)
        :returns:   List of the IPs of machines using aq images
         from machines with IPs starting with "172.16."
    """
    servers = ssh_command(
        openstack_client,
        "source admin-openrc.sh ; "
        "openstack server list --all-projects --long --limit -1 --ip=172.16. | "
        "grep -i '\\-aq'",
    )

    # Define the Regex expression used to find the IP address
    ip_rexp = re_compile(r"((?<=Internal=)([0-9](\.)?)+)")

    # Use Regex to find all instances of an IP address in the list of servers
    return ip_rexp.findall(str(servers))


def check_openstack_ip(aq_ip, aquilon_client, openstack_zombie_filepath):
    """
    Function to check the host of an AQ managed machine
        :param aq_ip: The IP to check (String)
        :param aquilon_client: Paramiko client (client)
        :param openstack_zombie_filepath: The filepath of the openstack output file (String)
        :returns:   The host of the AQ managed VM if it exists, otherwise False
    """
    ip_string = aq_ip.replace(".", "-")
    ip_string = "host-" + ip_string + ".nubes.stfc.ac.uk"
    aq_host = ssh_command(aquilon_client, "aq show_host --hostname " + ip_string)
    if "Not Found:" in str(aq_host):
        # If the VM doesn't have details in Aquilon, save its IP address as a potential zombie
        with open(openstack_zombie_filepath, "a") as openstack_zombie_file:
            openstack_zombie_file.write(ip_string + "\n")
        return False
    return aq_host


def check_aquilon_serial(aq_host, aq_ip, openstack_client, aquilon_zombie_filepath):
    """
    Function to check if a serial number of a VM matches that of the AQ host
        :param aq_host: The host of the VM (String)
        :param aq_ip: The IP to check (String)
        :param openstack_client: Paramiko client (client)
        :param aquilon_zombie_filepath: The filepath of the Aquilon output file (String)
    """
    # Define the Regex expression used to find the Serial number
    serial_rexp = re_compile(r"((?<=Serial: )(.+?)(?=\\r))")

    # Find the serial in the host information using Regex
    serial = serial_rexp.findall(str(aq_host))[0][0]

    # Get the host assigned to that serial in Openstack
    server_details = ssh_command(
        openstack_client, "source admin-openrc.sh ; openstack server show " + serial
    )

    if "No server with a name or ID of" in str(server_details):
        # If the serial doesn't return a host, save its serial and IP as a potential zombie
        with open(aquilon_zombie_filepath, "a") as aquilon_zombie_file:
            aquilon_zombie_file.write(serial + " | " + aq_ip + "\n")


def parse_args(inp_args):
    """
    Function to parse commandline args
    :param inp_args: a set of commandline args to parse (dict)
    :returns: A dictionary of parsed args
    """
    # Get arguments passed to the script
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-u", "--user", metavar="USER", help="FedID of the user", required=True
    )
    parser.add_argument(
        "-p",
        "--password",
        metavar="PASSWORD",
        help="Password of the user",
        required=True,
    )
    parser.add_argument(
        "-i",
        "--ip",
        metavar="IP",
        help="IP of the machine with Openstack to SSH to",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="OUTPUT",
        help="Directory to create the output files in",
        default="output",
    )
    args = parser.parse_args(inp_args)
    return args


def aq_zombie_finder():
    """
    Main Function to query aquilon to get a list of IPs of
    VMs with Aquilon images, check if VMs that no longer
    exist are still being managed by Aquilon or if VMs that
    should be managed by Aquilon aren't, then output the IPs
    into 2 files.
    """
    # Define the variables with the script arguments
    args = parse_args(sys.argv[1:])
    user = args.user
    password = args.password
    openstack_ip = args.ip
    output_location = args.output

    # Create a paramiko SSH client to the VM running Openstack and to Aquilon
    openstack_client = create_client(openstack_ip, user, password)
    aquilon_client = create_client("aquilon.gridpp.rl.ac.uk", user, password)

    # Ensure output directory exists
    Path(output_location).mkdir(exist_ok=True)

    # Define the filepath for the output to be saved to
    openstack_zombie_filepath = os.path.join(
        output_location, "openstack_zombie_list.txt"
    )
    aquilon_zombie_filepath = os.path.join(output_location, "aquilon_zombie_list.txt")

    # Check if output files already exist
    for filepath in [
        openstack_zombie_filepath,
        aquilon_zombie_filepath,
    ]:
        if os.path.exists(filepath):
            raise RuntimeError(f"{filepath} already exists")

    # Get a list of the IPs of AQ VMs
    aq_ips = get_aq_ips(openstack_client)

    # Run through each IP address found in the list of servers
    for i, aq_ip in enumerate(aq_ips, start=1):
        # Print the current progress through the list of IP addresses
        print(i, "/", len(aq_ips))

        # Check the ip of the Aquilon VM
        aq_host = check_openstack_ip(
            aq_ip[0], aquilon_client, openstack_zombie_filepath
        )

        # Check if an aquilon host exists
        if aq_host:
            # Check the serial number of the AQ host
            check_aquilon_serial(
                aq_host, aq_ip[0], openstack_client, aquilon_zombie_filepath
            )

    # Close the SSH clients
    openstack_client.close()
    aquilon_client.close()


if __name__ == "__main__":
    aq_zombie_finder()
