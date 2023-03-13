from pathlib import Path

from main import (
    generate_hosts,
    generate_ips,
    format_output,
    read_from_template,
    substitute_template,
    write_to_file,
)


def test_generate_100():
    """
    Test that the generate_hosts function returns a list of 255 hosts
    belonging to the 172.16.100.x network
    """
    result = generate_hosts(100)
    assert len(result) == 255
    assert "172.16.100.210" in result
    assert "172.16.100.0" in result


def test_generate_all_ips():
    """
    Test that the generate_ips function returns a list of 15 * 255 hosts
    corresponding to the 15 networks in the 172.16.100.x - 172.16.114.x range
    that the STFC Cloud uses
    """
    result = generate_ips()
    # 15 networks and 255 hosts per network
    expected_hosts = 15 * 255
    assert len(result) == expected_hosts


def test_format_ips():
    """
    Test that the format_output function returns a string with the correct
    format for the Prometheus config file
    """
    result = format_output()
    assert "    - 172.16.109.207:9100\n" in result
    assert "    - 172.16.114.254:9100\n" in result
    assert isinstance(result, str)


def test_read_from_file(tmp_path):
    """
    Test that the read_from_template function returns a string with the
    contents of the file passed to it
    """
    with open(tmp_path / "test.txt", "w") as f:
        f.write("TEMPLATE")
    result = read_from_template(tmp_path / "test.txt")
    assert "TEMPLATE" in result


def test_substitute_template():
    """
    Test that the substitute_template function returns a string with the
    correct replacement string in the correct place
    """
    input_str = "THIS IS MY TEMPLATE FOO"
    replacement_str = "new str"

    result = substitute_template(input_str, replacement_str)
    assert "THIS IS MY new str FOO" == result


def test_write_file():
    """
    Test that the write_to_file function writes the correct string to the
    correct file
    """
    tmp_path = Path("write_test.txt")
    output_text = "I wrote this"
    write_to_file(tmp_path, output_text)
    result = read_from_template(tmp_path)
    assert result == output_text

    tmp_path.unlink()
