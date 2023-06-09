import paramiko
from re import compile
from getpass import getpass


# Creates an SSH client through Paramiko with the users details and returns the client
def create_client(host, user, password):
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(hostname=host, username=user, password=password, timeout=60)
    return client


# Executes a command through a Paramiko client, waits for an exit status and outputs the response
def ssh_command(client, command):
    _, _stdout, _ = client.exec_command(command, get_pty=True, timeout=60)
    _stdout.channel.recv_exit_status()
    return _stdout.readlines()


# Return a list of the IPs from AQ manage VMs
def get_aq_ips(openstack_client):
    # Run a command on the openstack VM to get a list of
    # all servers with "-aq" in their details that start with "172.16"
    servers = ssh_command(
        openstack_client,
        "source admin-openrc.sh ; "
        "openstack server list --all-projects --long --limit -1 --ip=172.16 | "
        "grep -i '\\-aq'",
    )

    # Define the Regex expression used to find the IP address
    ip_rexp = compile(r"((?<=Internal=)([0-9](\.)?)+)")

    # Use Regex to find all instances of an IP address in the list of servers
    return ip_rexp.findall(str(servers))


# Check if an AQ host exists for an AQ managed VM and if so, return the host
def check_openstack_ip(aq_ip, aquilon_client, openstack_zombie_file):
    # Format the IP address and check the host information of the VM at that IP address in Aquilon
    ip_string = aq_ip.replace(".", "-")
    ip_string = "host-" + ip_string + ".nubes.stfc.ac.uk"
    aq_host = ssh_command(aquilon_client, "aq show_host --hostname " + ip_string)

    if "Not Found:" in str(aq_host):
        # If the VM doesn't have details in Aquilon, save its IP address as a potential zombie
        openstack_zombie_file.write(ip_string + "\n")
        return False

    else:
        return aq_host


# Check if the serial number matches the host
def check_aquilon_serial(aq_host, aq_ip, openstack_client, aquilon_zombie_file):
    # Define the Regex expression used to find the Serial number
    serial_rexp = compile(r"((?<=Serial: )(.+?)(?=\\r))")

    # Find the serial in the host information using Regex
    serial = serial_rexp.findall(str(aq_host))[0][0]

    # Get the host assigned to that serial in Openstack
    server_details = ssh_command(
        openstack_client, "source admin-openrc.sh ; openstack server show " + serial
    )

    if "No server with a name or ID of" in str(server_details):
        # If the serial doesn't return a host, save its serial and IP as a potential zombie
        aquilon_zombie_file.write(serial + " | " + aq_ip + "\n")


def aq_zombie_finder():
    # Prompt the user for their FedID, Password and Openstack IP to connect to
    user = input("FedID: ")
    password = getpass("Password: ")
    openstack_ip = input("Openstack IP: ")

    # Create a paramiko SSH client to the VM running Openstack and to Aquilon
    openstack_client = create_client(openstack_ip, user, password)
    aquilon_client = create_client("aquilon.gridpp.rl.ac.uk", user, password)

    # Create a blank text documents for the output to be saved to
    open("output\\openstack_zombie_list.txt", "w").close()
    open("output\\aquilon_zombie_list.txt", "w").close()
    openstack_zombie_file = open("output\\openstack_zombie_list.txt", "a")
    aquilon_zombie_file = open("output\\aquilon_zombie_list.txt", "a")

    # Get a list of the IPs of AQ VMs
    aq_ips = get_aq_ips(openstack_client)

    # Run through each IP address found in the list of servers
    for i, aq_ip in enumerate(aq_ips, start=1):
        # Print the current progress through the list of IP addresses
        print(i, "/", len(aq_ips))

        # Check the ip of the Aquilon VM
        aq_host = check_openstack_ip(aq_ip[0], aquilon_client, openstack_zombie_file)

        # Check if an aquilon host exists
        if aq_host:
            # Check the serial number of the AQ host
            check_aquilon_serial(
                aq_host, aq_ip[0], openstack_client, aquilon_zombie_file
            )

    # Close the SSH clients
    openstack_client.close()
    aquilon_client.close()

    # Close the text files
    openstack_zombie_file.close()
    aquilon_zombie_file.close()


if __name__ == "__main__":
    aq_zombie_finder()
