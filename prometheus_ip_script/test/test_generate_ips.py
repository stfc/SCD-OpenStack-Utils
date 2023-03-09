from pathlib import Path

from main import generate_hosts, generate_ips, format_output, read_from_template, substitute_template, write_to_file


def test_generate_100():
    result = generate_hosts(100)
    assert len(result) == 255
    assert "172.16.100.210" in result
    assert "172.16.100.0" in result


def test_generate_all_ips():
    result = generate_ips()
    # 15 networks and 255 hosts per network
    expected_hosts = 15 * 255
    assert len(result) == expected_hosts


def test_format_ips():
    result = format_output()
    assert "    - 172.16.109.207:9100\n" in result
    assert "    - 172.16.114.254:9100\n" in result
    assert isinstance(result, str)


def test_read_from_file():
    file_name = Path("../template.txt")
    result = read_from_template(file_name)
    assert "    - localhost:9090" in result


def test_substitute_template():
    input_str = "THIS IS MY TEMPLATE FOO"
    replacement_str = "new str"

    result = substitute_template(input_str, replacement_str)
    assert "THIS IS MY new str FOO" == result


def test_write_file():
    tmp_path = Path("write_test.txt")
    output_text = "I wrote this"
    write_to_file(tmp_path, output_text)
    result = read_from_template(tmp_path)
    assert result == output_text

    tmp_path.unlink()
