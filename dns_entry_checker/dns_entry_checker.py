import argparse
import os
import sys
import paramiko

from collections import defaultdict
from re import compile

# Define the Regex used to identify IPs
IP_REXP = compile(r"(([0-9]{1,3}[.-]){3}[0-9]{1,3})")


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
    _stdin, _stdout, _stderr = client.exec_command(command, get_pty=True, timeout=60)
    _stdout.channel.recv_exit_status()
    return _stdout.readlines()


def find_ip_dns_pair(command_output):
    """
    Function to get the IP and DNS from the SSH command output
        :param command_output: Output of the command to check DNS names (string)
        :returns: List containing the matching IP and DNS
    """
    ip_dns_found = IP_REXP.findall(command_output)
    return [ip_dns_found[0][0], ip_dns_found[1][0]]


def populate_ip_dict(ips_dns_pair, order_check_dict):
    """
    Function to populate the order_check_dict
        :param ips_dns_pair: List containing IP and matching DNS (string)
        :param order_check_dict: Dictionary containing an IPs third byte as a key,
        and list of fourth bytes as an item (defaultdict)
    """
    last_rexp = compile(r"([0-9]{1,3}\.[0-9]{1,3}(?!.))")

    order_values = last_rexp.findall(ips_dns_pair[1])[0].split(".")
    order_check_dict[order_values[0]].append(order_values[1])


def check_ip_dns_mismatch(
    ips_dns_pair,
    client,
    backward_mismatch_filepath,
    forward_mismatch_filepath,
    backward_missing_filepath,
):
    """
    Function to check if a DNS matches its IP
        :param ips_dns_pair: List containing IP and matching DNS (string)
        :param client: Paramiko client (client)
        :param backward_mismatch_filepath: The filepath of the backward mismatch output file (String)
        :param forward_mismatch_filepath: The filepath of the forward mismatch output file (String)
        :param backward_missing_filepath: The filepath of the backward missing output file (String)
        :returns: List containing the matching IP and DNS
    """
    if not ips_dns_pair[0].replace("-", ".") == ips_dns_pair[1]:
        with open(forward_mismatch_filepath, "a") as forward_mismatch_file:
            forward_mismatch_file.write(f"{ips_dns_pair[1]}\n")
        return
    returned_dns = ssh_command(client, "dig -x {s} +short".format(s=ips_dns_pair[1]))
    if not returned_dns:
        with open(backward_missing_filepath, "a") as backward_missing_file:
            backward_missing_file.write(f"{ips_dns_pair[1]}\n")
        return
    backward_ip = IP_REXP.findall(returned_dns[0])
    if not backward_ip:
        with open(backward_missing_filepath, "a") as backward_missing_file:
            backward_missing_file.write(f"{ips_dns_pair[1]}\n")
    elif not backward_ip[0][0] == ips_dns_pair[0]:
        with open(backward_mismatch_filepath, "a") as backward_mismatch_file:
            backward_mismatch_file.write(f"{ips_dns_pair[1]}\n")


def check_missing_ips(key, gap_missing_filepath):
    """
    Function to check which IPs are missing from 2-254 and output them to a file
        :param key: List containing (List)
        :param gap_missing_filepath: The filepath of the gap missing output file (String)
    """
    res = set([eval(j) for j in key[1]])
    missing_values = [k for k in (range(2, 255)) if k not in res]
    for ip_last_byte in missing_values:
        with open(gap_missing_filepath, "a") as gap_missing_file:
            gap_missing_file.write(f"172.16.{key[0]}.{ip_last_byte}\n")


def parse_args(inp_args):
    """
    Function to parse commandline args
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
        help="IP of the machine to SSH to",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="OUTPUT",
        help="Directory to create the output files in",
    )
    args = parser.parse_args(inp_args)
    return args


def dns_entry_checker():
    # Define the variables with the script arguments
    args = parse_args(sys.argv[1:])
    user = args.user
    password = args.password
    ip = args.ip
    output = args.output

    # Create an SSH client with the credentials given
    client = create_client(ip, user, password)

    # Run a command on the VM to get all IP addresses with their domain names
    command_outputs = ssh_command(
        client,
        "dig @ns1.rl.ac.uk stfc.ac.uk  axfr | "
        "grep -i nubes.stfc.ac.uk | "
        "grep -v CNAME | "
        "grep '172.16.'",
    )

    # Define the filepath for the output to be saved to
    forward_mismatch_filepath = os.path.join(
        output or "output", "forward_mismatch_list.txt"
    )
    backward_mismatch_filepath = os.path.join(
        output or "output", "backward_mismatch_list.txt"
    )
    backward_missing_filepath = os.path.join(
        output or "output", "backward_missing_list.txt"
    )
    gap_missing_filepath = os.path.join(output or "output", "gap_missing_list.txt")

    # Check if output files already exist
    for filepath in [
        forward_mismatch_filepath,
        backward_mismatch_filepath,
        backward_missing_filepath,
        gap_missing_filepath,
    ]:
        if os.path.exists(filepath):
            raise RuntimeError(f"{filepath} already exists")

    # Create a dictionary to store IPs for checking gaps
    order_check_dict = defaultdict(list)

    # Check through all IP and DNS pairs received
    for i, command_output in enumerate(command_outputs):
        print(i + 1, "/", len(command_outputs))

        ips_dns_pair = find_ip_dns_pair(command_output)
        populate_ip_dict(ips_dns_pair, order_check_dict)

        check_ip_dns_mismatch(
            ips_dns_pair,
            client,
            backward_mismatch_filepath,
            forward_mismatch_filepath,
            backward_missing_filepath,
        )

    # Check through all IP addresses received for gaps
    for i, key in enumerate(order_check_dict.items()):
        check_missing_ips(key, gap_missing_filepath)

    # Close the Client
    client.close()


if __name__ == "__main__":
    dns_entry_checker()
