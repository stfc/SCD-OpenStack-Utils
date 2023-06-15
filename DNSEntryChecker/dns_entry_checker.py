import paramiko
from re import compile
from getpass import getpass
from collections import defaultdict


# Creates an SSH client through Paramiko with the users details and returns the client
def create_client(host, user, password):
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(hostname=host, username=user, password=password, timeout=60)
    return client


# Executes a command through a Paramiko client, waits for an exit status and outputs the response
def ssh_command(client, command):
    _stdin, _stdout, _stderr = client.exec_command(command, get_pty=True, timeout=60)
    _stdout.channel.recv_exit_status()
    return _stdout.readlines()


# Checks if the IP address and DNS match
def pair_ip_and_dns(dns_pair, order_check_dict, ip_rexp):
    last_rexp = compile(r"([0-9]{1,3}\.[0-9]{1,3}(?!.))")

    ips = ip_rexp.findall(dns_pair)
    ips = [ips[0][0], ips[1][0]]

    order_values = last_rexp.findall(ips[1])[0].split(".")
    order_check_dict[order_values[0]].append(order_values[1])
    return ips


# Checks if the DNS returns the matching IP
def check_ip_dns_mismatch(
    ips,
    client,
    ip_rexp,
    backward_mismatch_file,
    forward_mismatch_file,
    backward_missing_file,
):
    if ips[0].replace("-", ".") == ips[1]:
        returned_dns = ssh_command(client, "dig -x {s} +short".format(s=ips[1]))
        if returned_dns:
            backward_ip = ip_rexp.findall(returned_dns[0])
            if not backward_ip:
                backward_missing_file.write(f"{ips[1]}\n")
            elif not backward_ip[0][0] == ips[0]:
                backward_mismatch_file.write(f"{ips[1]}\n")
        else:
            backward_missing_file.write(f"{ips[1]}\n")
    else:
        forward_mismatch_file.write(f"{ips[1]}\n")


# Checks which IPs are missing from 2-254
def check_missing_ips(key, gap_missing_file, i):
    res = set([eval(j) for j in key[1]])
    missing_values = [k for k in sorted(set(range(2, 255))) if k not in res]
    for ip in missing_values:
        gap_missing_file.write(f"172.16.{i + 100}.{ip}\n")


def dns_entry_checker():
    # Prompt the user for their FedID, Password and IP to connect to
    user = input("FedID: ")
    password = getpass("Password: ")
    ip = input("IP: ")

    # Create an SSH client with the credentials given
    client = create_client(ip, user, password)

    # Run a command on the VM to get all IP addresses with their domain names
    dns_list = ssh_command(
        client,
        "dig @ns1.rl.ac.uk stfc.ac.uk  axfr | "
        "grep -i nubes.stfc.ac.uk | "
        "grep -v CNAME | "
        "grep '172.16.105'",
    )

    # Create or clear, then open to append to, the output files
    open("output\\forward_mismatch_list.txt", "w").close()
    open("output\\backward_mismatch_list.txt", "w").close()
    open("output\\forward_missing_list.txt", "w").close()
    open("output\\backward_missing_list.txt", "w").close()
    open("output\\gap_missing_list.txt", "w").close()
    forward_mismatch_file = open("output\\forward_mismatch_list.txt", "a")
    backward_mismatch_file = open("output\\backward_mismatch_list.txt", "a")
    forward_missing_file = open("output\\forward_missing_list.txt", "a")
    backward_missing_file = open("output\\backward_missing_list.txt", "a")
    gap_missing_file = open("output\\gap_missing_list.txt", "a")

    # Define the Regex used to identify IPs
    ip_rexp = compile(r"(([0-9]{1,3}[.-]){3}[0-9]{1,3})")

    # Create a dictionary to store IPs for checking gaps
    order_check_dict = defaultdict(list)

    # Check through all IP and DNS pairs received
    for i, dns_pair in enumerate(dns_list):
        print(i + 1, "/", len(dns_list))

        ips = pair_ip_and_dns(dns_pair, order_check_dict, ip_rexp)

        check_ip_dns_mismatch(
            ips,
            client,
            ip_rexp,
            backward_mismatch_file,
            forward_mismatch_file,
            backward_missing_file,
        )

    # Check through all IP addresses received for gaps
    for i, key in enumerate(order_check_dict.items()):
        check_missing_ips(key, gap_missing_file, i)

    # Close the Client and output files
    client.close()
    forward_mismatch_file.close()
    backward_mismatch_file.close()
    forward_missing_file.close()
    backward_missing_file.close()
    gap_missing_file.close()


if __name__ == "__main__":
    dns_entry_checker()
