# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
from ipaddress import IPv4Network
from pathlib import Path
from typing import List


def main() -> None:
    """
    Generates a list of IP addresses based on the STFC Cloud network range
    and writes them to a file in the correct format for the Prometheus.
    """
    config_contents = read_from_template(Path("template.txt"))
    ip_list = format_output()
    new_file_contents = substitute_template(config_contents, ip_list)
    write_to_file(Path("prometheus-config.yml.template"), new_file_contents)


def read_from_template(file_path: Path) -> str:
    """
    Read the contents of a file and return them as a string
    :param file_path: Path to the file to read
    :return: String containing the contents of the file
    """
    with open(file_path) as file:
        return file.read()


def substitute_template(template: str, replacement: str) -> str:
    """
    Replace the string "TEMPLATE" in the template with the replacement
    string.
    :param template: Input string containing the string "TEMPLATE" to replace
    :param replacement: The replacement string which will overwrite the "TEMPLATE" string
    :return: The string with replacement in place of "TEMPLATE"
    """
    return template.replace("TEMPLATE", replacement)


def write_to_file(file_path: Path, content: str) -> None:
    """
    Write the content string to the file at the file_path
    :param file_path: The file to write to
    :param content: The string to write to the file
    """
    with open(file_path, "w+") as file:
        file.write(content)


def generate_hosts(network: int) -> List[str]:
    """
    Generate a list of IP addresses for the hosts in a given network
    :param network: The third octet of the network to generate hosts for
    :return: A list of string IP addresses for the given net
    """
    return [str(ip) for ip in IPv4Network(f"172.16.{network}.0/24")][:-1]


def generate_ips() -> List[str]:
    """
    Generate a list of IP addresses for the hosts in the STFC Cloud network
    :return: The list of IP addresses as strings
    """
    result = []
    for i in range(100, 115):
        result.extend(generate_hosts(i))
    return result


def format_output() -> str:
    """
    Format the output of the generate_ips function into a string with the
    correct format for the Prometheus config file
    :return: A single string in the correct format for the Prometheus config
    """
    final_result = []
    for i in generate_ips():
        final_result.append(f"    - {i}:9100\n")
    return "".join(final_result)


if __name__ == "__main__":
    main()
