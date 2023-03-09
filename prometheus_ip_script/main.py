from ipaddress import IPv4Network
from pathlib import Path
from typing import List


def main():
    config_contents = read_from_template(Path("template.txt"))
    ip_list = format_output()
    new_file_contents = substitute_template(config_contents, ip_list)
    write_to_file(Path("prometheus-config.yml.template"), new_file_contents)


def read_from_template(file_path: Path):
    with open(file_path) as file:
        return file.read()


def substitute_template(template: str, replacement: str) -> str:
    return template.replace("TEMPLATE", replacement)


def write_to_file(file_path: Path, content: str):
    with open(file_path, "w+") as file:
        file.write(content)


def generate_hosts(network: int) -> List[str]:
    return [str(ip) for ip in IPv4Network(f"172.16.{network}.0/24")][:-1]


def generate_ips() -> List[str]:
    result = []
    for i in range(100, 115):
        result.extend(generate_hosts(i))
    return result


def format_output() -> str:
    final_result = []
    for i in generate_ips():
        final_result.append(f"    - {i}:9100\n")
    return "".join(final_result)


if __name__ == "__main__":
    main()
