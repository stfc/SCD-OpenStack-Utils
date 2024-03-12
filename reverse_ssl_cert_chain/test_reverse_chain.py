"""
This test file should test all the functions in the reverse_chain file.
"""

from pathlib import Path
from unittest.mock import patch, mock_open
from pytest import fixture

# Disabling this pylint error as there is only a single python file.
# pylint: disable=import-error
import reverse_chain


@fixture(scope="function", name="mock_path")
def mock_path_fixture():
    """
    This fixture provides a mock path.
    """
    return Path("/some/mock/path")


@fixture(scope="function", name="mock_file_certificate")
def mock_certificate_file_fixture():
    """
    This fixture provides a mock certificate file.
    """
    certificate_str = (
        "-----BEGIN CERTIFICATE-----\n"
        "somecertificatejunk1"
        "somecertificatejunk2"
        "-----END CERTIFICATE-----\n"
        "-----BEGIN CERTIFICATE-----\n"
        "somecertificatejunkA"
        "somecertificatejunkB"
        "-----END CERTIFICATE-----\n"
    )
    return certificate_str


@fixture(scope="function", name="mock_certificate_list")
def mock_certificate_list_fixture():
    """
    This fixture provides a list containing mock certificate file lines.
    """
    certificate_list = [
        "-----BEGIN CERTIFICATE-----\n",
        "somecertificatejunk1",
        "somecertificatejunk2",
        "-----END CERTIFICATE-----\n",
        "-----BEGIN CERTIFICATE-----\n",
        "somecertificatejunkA",
        "somecertificatejunkB",
        "-----END CERTIFICATE-----\n",
    ]
    return certificate_list


@fixture(scope="function", name="mock_certificate_list_no_eof_newline")
def mock_certificate_list_no_eof_newline_fixture():
    """
    This fixture provides a list containing mock certificate file lines
    with not end of file new line.
    """
    certificate_list = [
        "-----BEGIN CERTIFICATE-----\n",
        "somecertificatejunk1",
        "somecertificatejunk2",
        "-----END CERTIFICATE-----\n",
        "-----BEGIN CERTIFICATE-----\n",
        "somecertificatejunkA",
        "somecertificatejunkB",
        "-----END CERTIFICATE-----",
    ]
    return certificate_list


@fixture(scope="function", name="mock_crt_block_list")
def mock_crt_block_list_fixture():
    """
    This fixture provides a mock list with sub lists of mock certificates.
    """
    mock_crt_block_list = [
        [
            "-----BEGIN CERTIFICATE-----\n",
            "somecertificatejunk1",
            "somecertificatejunk2",
            "-----END CERTIFICATE-----\n",
        ],
        [
            "-----BEGIN CERTIFICATE-----\n",
            "somecertificatejunkA",
            "somecertificatejunkB",
            "-----END CERTIFICATE-----\n",
        ],
    ]
    return mock_crt_block_list


def test_read_crt(mock_path):
    """
    This test ensures the open function is called and the readlines method is called.
    """
    with patch(
        "reverse_chain.open", mock_open(read_data="line1\nline2\n")
    ) as mock_open_ctx:
        res = reverse_chain.read_crt(mock_path)
        mock_open_ctx.assert_called_once_with(mock_path, "r", encoding="utf-8")
        mock_open_ctx.return_value.readlines.assert_called_once()
        assert res == ["line1\n", "line2\n"]


def test_construct_blocks(mock_certificate_list_no_eof_newline):
    """
    This test ensures that the certificate files are put into correct blocks.
    """
    res = reverse_chain.construct_blocks(mock_certificate_list_no_eof_newline)
    assert res == [
        [
            "-----BEGIN CERTIFICATE-----\n",
            "somecertificatejunk1",
            "somecertificatejunk2",
            "-----END CERTIFICATE-----\n",
        ],
        [
            "-----BEGIN CERTIFICATE-----\n",
            "somecertificatejunkA",
            "somecertificatejunkB",
            "-----END CERTIFICATE-----\n",
        ],
    ]


def test_construct_blocks_no_eof_newline(mock_certificate_list_no_eof_newline):
    """
    This test ensures the certificate files are put into correct blocks when there
    is no newline at the end of the file.
    """
    res = reverse_chain.construct_blocks(mock_certificate_list_no_eof_newline)
    assert res == [
        [
            "-----BEGIN CERTIFICATE-----\n",
            "somecertificatejunk1",
            "somecertificatejunk2",
            "-----END CERTIFICATE-----\n",
        ],
        [
            "-----BEGIN CERTIFICATE-----\n",
            "somecertificatejunkA",
            "somecertificatejunkB",
            "-----END CERTIFICATE-----\n",
        ],
    ]


def test_reverse_blocks(mock_crt_block_list):
    """
    This test ensures that the lists are reversed properly.
    """
    reversed_blocks = [
        [
            "-----BEGIN CERTIFICATE-----\n",
            "somecertificatejunkA",
            "somecertificatejunkB",
            "-----END CERTIFICATE-----\n",
        ],
        [
            "-----BEGIN CERTIFICATE-----\n",
            "somecertificatejunk1",
            "somecertificatejunk2",
            "-----END CERTIFICATE-----\n",
        ],
    ]
    res = reverse_chain.reverse_blocks(mock_crt_block_list)
    assert res == reversed_blocks


def test_read_key(mock_path):
    """
    This test ensures the open function is called and the read method is called.
    """
    with patch(
        "reverse_chain.open", mock_open(read_data="somemockkey")
    ) as mock_open_ctx:
        res = reverse_chain.read_key(mock_path)
        mock_open_ctx.assert_called_once_with(mock_path, "r", encoding="utf-8")
        mock_open_ctx.return_value.read.assert_called_once()
        assert res == "somemockkey"


def test_prepend_key_to_crt(mock_crt_block_list):
    """
    This test ensures the key string as prepended to the certificate list.
    """
    mock_key = "somemockkey"
    res = reverse_chain.prepend_key_to_crt(mock_crt_block_list, mock_key)
    assert res == ([mock_key] + mock_crt_block_list)


def test_construct_file(mock_crt_block_list):
    """
    This test ensures the open function is called to write to the file.
    """
    with patch("reverse_chain.open") as mock_open_ctx:
        reverse_chain.construct_file(mock_crt_block_list)
        mock_open_ctx.assert_called_once_with("full_chain.pem", "w", encoding="utf-8")


# Disabling this pylint error as I am testing the main function.
# pylint: disable=too-many-arguments
@patch("reverse_chain.read_crt")
@patch("reverse_chain.read_key")
@patch("reverse_chain.construct_blocks")
@patch("reverse_chain.reverse_blocks")
@patch("reverse_chain.prepend_key_to_crt")
@patch("reverse_chain.construct_file")
def test_main_add_key(
    mock_construct_file,
    mock_prepend_key_to_crt,
    mock_reverse_blocks,
    mock_construct_blocks,
    mock_read_key,
    mock_read_crt,
    mock_path,
):
    """
    This test ensures the main functions calls all the methods appropriately
     with the correct arguments. It also tests if the prepend key function
    is called when add_key is true.
    """
    reverse_chain.main(mock_path, mock_path, True)
    mock_read_crt.assert_called_once_with(mock_path)
    mock_read_key.assert_called_once_with(mock_path)
    mock_construct_blocks.assert_called_once_with(mock_read_crt.return_value)
    mock_reverse_blocks.assert_called_once_with(mock_construct_blocks.return_value)
    mock_prepend_key_to_crt.assert_called_once_with(
        mock_reverse_blocks.return_value, mock_read_key.return_value
    )
    mock_construct_file.assert_called_once_with(mock_prepend_key_to_crt.return_value)
