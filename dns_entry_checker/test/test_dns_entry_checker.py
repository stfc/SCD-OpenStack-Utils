import dns_entry_checker
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch, NonCallableMock, call
from parameterized import parameterized
from dns_entry_checker import (
    create_client,
    ssh_command,
    find_ip_dns_pair,
    check_ip_dns_mismatch,
    check_missing_ips,
)


class DNSEntryCheckerTests(unittest.TestCase):
    @patch("dns_entry_checker.paramiko")
    def test_create_client(self, mock_paramiko):
        host = "test.aquilon.gridpp.rl.ac.uk"
        user = "test.abc12345"
        password = "test.A4gdfGs"

        mock_client = MagicMock()
        mock_paramiko.client.SSHClient.return_value = mock_client
        mock_paramiko.client.set_missing_host_key_policy = MagicMock()
        mock_paramiko.AutoAddPolicy = NonCallableMock()
        mock_paramiko.connect = MagicMock()

        client = create_client(host, user, password)

        client.connect.assert_called_once_with(
            hostname=host, username=user, password=password, timeout=60
        )

        self.assertEqual(client, mock_client)

    def test_ssh_command(self):
        mock_client = MagicMock()
        command = "test aq show_host --hostname localhost"

        mock_stdout = MagicMock()
        mock_client.exec_command.return_value = MagicMock(), mock_stdout, MagicMock()
        mock_stdout.channel.recv_exit_status.return_value = NonCallableMock()
        mock_stdout.readlines.return_value = NonCallableMock()

        command_output = ssh_command(mock_client, command)

        mock_client.exec_command.assert_called_once_with(
            command, get_pty=True, timeout=60
        )
        mock_stdout.channel.recv_exit_status.assert_called_once()
        mock_stdout.readlines.assert_called_once()

        self.assertEqual(command_output, mock_stdout.readlines.return_value)

    def test_pair_ip_and_dns(self):
        dns_pair = "test-host-172-16-1-1.nubes.stfc.ac.uk 7200 IN A\t172.16.1.1\r\n"

        command_output = find_ip_dns_pair(dns_pair)
        self.assertEqual(command_output[0].replace("-", "."), command_output[1])

    @parameterized.expand(
        [
            ("IPs match", ["172-16-1-1", "172.16.1.1"], True),
            ("IPs don't match", ["172-16-1-1", "172.16.1.0"], False),
        ]
    )
    @mock.patch("builtins.open")
    def test_check_ip_dns_mismatch(self, name, returned_ips, expected_out, mock_file):
        ips_dns_pair = returned_ips
        client = MagicMock()
        backward_mismatch_filepath = "test/backward/mismatch/filepath"
        forward_mismatch_filepath = "test/forward/mismatch/filepath"
        backward_missing_filepath = "test/backward/missing/filepath"

        with patch("dns_entry_checker.ssh_command"):
            dns_entry_checker.ssh_command.return_value = []

            check_ip_dns_mismatch(
                ips_dns_pair,
                client,
                backward_mismatch_filepath,
                forward_mismatch_filepath,
                backward_missing_filepath,
            )

        if expected_out:
            assert (
                call("test/forward/mismatch/filepath", "a") not in mock_file.mock_calls
            )
        else:
            assert call("test/forward/mismatch/filepath", "a") in mock_file.mock_calls

    @parameterized.expand(
        [
            ("DNS returned", ["test-host-172-16-1-1.nubes.stfc.ac.uk"], True),
            ("DNS not returned", [], False),
        ]
    )
    @mock.patch("builtins.open")
    def test_check_ip_dns_mismatch_dns_returned(
        self, name, returned_dns, expected_out, mock_file
    ):
        ips_dns_pair = ["172-16-1-1", "172.16.1.1"]
        client = MagicMock()
        backward_mismatch_filepath = "test/backward/mismatch/filepath"
        forward_mismatch_filepath = "test/forward/mismatch/filepath"
        backward_missing_filepath = "test/backward/missing/filepath"

        with patch("dns_entry_checker.ssh_command"):
            dns_entry_checker.ssh_command.return_value = returned_dns

            check_ip_dns_mismatch(
                ips_dns_pair,
                client,
                backward_mismatch_filepath,
                forward_mismatch_filepath,
                backward_missing_filepath,
            )

        if not expected_out:
            assert call("test/backward/missing/filepath", "a") in mock_file.mock_calls
        else:
            assert (
                call("test/backward/missing/filepath", "a") not in mock_file.mock_calls
            )

    @parameterized.expand(
        [
            ("Return doesn't contain IP", ["No IPS here"], 0),
            ("Returned IP doesn't match", ["test-host-172-16-1-2.nubes.stfc.ac.uk"], 1),
            ("Returned IP matches", ["test-host-172-16-1-1.nubes.stfc.ac.uk"], 2),
        ]
    )
    @mock.patch("builtins.open")
    def test_check_ip_dns_mismatch_backwards_not_found(
        self,
        name,
        returned_ips,
        expected_out,
        mock_file,
    ):
        ips = ["172-16-1-1", "172.16.1.1"]
        client = MagicMock()
        backward_mismatch_filepath = "test/backward/mismatch/filepath"
        forward_mismatch_filepath = "test/forward/mismatch/filepath"
        backward_missing_filepath = "test/backward/missing/filepath"

        with patch("dns_entry_checker.ssh_command"):
            dns_entry_checker.ssh_command.return_value = returned_ips

            check_ip_dns_mismatch(
                ips,
                client,
                backward_mismatch_filepath,
                forward_mismatch_filepath,
                backward_missing_filepath,
            )

        if expected_out == 0:
            assert call("test/backward/missing/filepath", "a") in mock_file.mock_calls
        elif expected_out == 1:
            assert call("test/backward/mismatch/filepath", "a") in mock_file.mock_calls
        else:
            assert (
                call("test/backward/mismatch/filepath", "a") not in mock_file.mock_calls
            )
            assert (
                call("test/backward/missing/filepath", "a") not in mock_file.mock_calls
            )

    @parameterized.expand(
        [
            ("Gaps", [5], True),
            ("No gaps", sorted(set(range(2, 255))), False),
        ]
    )
    @mock.patch("builtins.open")
    def test_check_missing_ips(self, name, ips, expected_out, mock_file):
        key = ("105", [str(x).zfill(0) for x in ips])
        gap_missing_filepath = "test/gap/missing/filepath"

        check_missing_ips(key, gap_missing_filepath)

        print(expected_out, mock_file.mock_calls)

        if expected_out:
            assert call("test/gap/missing/filepath", "a") in mock_file.mock_calls
        else:
            assert call("test/gap/missing/filepath", "a") not in mock_file.mock_calls


if __name__ == "__main__":
    unittest.main()
