"""
If you have a SSL certificate with the full chain from root CA to you,
then you can use this script to reverse the chain order. Also, the
private key is prepended to the top of the chain.
If you do not need the private key to be added to the chain you can
use the script with the flag "--no-key".

Usage: python3 <path_to_cert> <path_to_key>
Optional: --no-key , Use this when do not want to prepend the key.
"""

from typing import List
from pathlib import Path
from sys import argv


def read_crt(crt: Path) -> List[str]:
    """
    Reads the lines from the file and stores each line as an element to a list.
    :param crt: Path to the certificate
    :return: A list where each element is a line from the file
    """
    with open(crt, "r", encoding="utf-8") as file:
        file_lines = file.readlines()
    return file_lines


def construct_blocks(file_lines: List[str]) -> List[List]:
    """
    Creates a new list where each element is a single certificate.
    It checks for the "BEGIN CERTIFICATE" then adds all proceeding
    lines to a list and stops when it meets "END CERTIFICATE".
    :param file_lines: A list where each element is a line from the file
    :return: A list where each element is a list of lines containing a single certificate
    """
    blocks = []
    current_block = []
    for line in file_lines:
        if line == "-----BEGIN CERTIFICATE-----\n":
            current_block = [line]
        elif line == "-----END CERTIFICATE-----\n":
            current_block.append(line)
            blocks.append(current_block)
        elif line == "-----END CERTIFICATE-----":
            current_block.append((line + "\n"))
            blocks.append(current_block)
        elif line == "\n":
            pass
        else:
            current_block.append(line)
    return blocks


def reverse_blocks(blocks: List[List]) -> List[List]:
    """
    Reverses the order of the list.
    :param blocks: A list where each element is a list representing a single certificate
    :return: The same list as blocks just reversed
    """
    blocks.reverse()
    return blocks


def read_key(key: Path) -> str:
    """
    Reads the contents of the key file into a single string.
    :param key: The path to the key file
    :return: A string containing the entire key
    """
    with open(key, "r", encoding="utf-8") as file:
        file_data = file.read()
    return file_data


def prepend_key_to_crt(crt: List[List], key: str) -> List[List]:
    """
    Adds the key to the top of the certificate chain
    :param crt: A list containing the certificates
    :param key: The key string
    :return: A list containing the key then all proceeding certificates
    """
    full_chain_list = [key] + crt
    return full_chain_list


def construct_file(full_chain_list: List[List]):
    """
    Writes all the lines in the list and subsequent lists into a file on the system.
    :param full_chain_list: A list containing the key and certificates
    """
    with open("full_chain.pem", "w", encoding="utf-8") as file:
        for block in full_chain_list:
            file.writelines(block)


def main(crt: Path, key: Path, add_key: bool):
    """
    This method calls all the above functions in order to reverse the supplied certificate chain.
    If the add_key parameter is true it will add the key to the top of the certificate chain.
    :param crt: Path to the certificate chain
    :param key: Path to the key file
    :param add_key: Whether to add the key to the chain or not
    """
    crt_data = read_crt(crt)
    key_data = read_key(key)
    crt_blocks = construct_blocks(crt_data)
    full_chain_list = reverse_blocks(crt_blocks)
    if add_key:
        full_chain_list = prepend_key_to_crt(full_chain_list, key_data)
    construct_file(full_chain_list)


if __name__ == "__main__":
    # Collect the command line arguments and passes them to the main function.
    args = argv[1:]
    crt_path = Path(args[0])
    key_path = Path(args[1])
    if "--no-key" in args:
        main(crt_path, key_path, False)
    else:
        main(crt_path, key_path, True)
