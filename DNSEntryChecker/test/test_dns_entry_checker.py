import unittest
from re import compile
from unittest.mock import MagicMock, patch, NonCallableMock
from parameterized import parameterized
from collections import defaultdict

import dns_entry_checker
from dns_entry_checker import (
    create_client,
    ssh_command,
    pair_ip_and_dns,
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
        order_check_dict = defaultdict(list)
        ip_rexp = compile(r"(([0-9]{1,3}[.-]){3}[0-9]{1,3})")

        command_output = pair_ip_and_dns(dns_pair, order_check_dict, ip_rexp)
        self.assertEqual(command_output[0].replace('-', '.'), command_output[1])

    @parameterized.expand(
        [
            ("IPs match", ["172-16-1-1", "172.16.1.1"], True),
            ("IPs don't match", ["172-16-1-1", "172.16.1.0"], False),
        ]
    )
    def test_check_ip_dns_mismatch(self, name, returned_ips, expected_out):
        ips = returned_ips
        client = MagicMock()
        ip_rexp = compile(r"(([0-9]{1,3}[.-]){3}[0-9]{1,3})")
        backward_mismatch_file = MagicMock()
        forward_mismatch_file = MagicMock()
        backward_missing_file = MagicMock()

        with patch("dns_entry_checker.ssh_command"):
            dns_entry_checker.ssh_command.return_value = []

            check_ip_dns_mismatch(ips, client, ip_rexp, backward_mismatch_file, forward_mismatch_file,
                                  backward_missing_file)

        if expected_out:
            forward_mismatch_file.write.assert_not_called()
        else:
            forward_mismatch_file.write.assert_called_once()

    @parameterized.expand(
        [
            ("DNS returned", ["test-host-172-16-1-1.nubes.stfc.ac.uk"], True),
            ("DNS not returned", [], False),
        ]
    )
    def test_check_ip_dns_mismatch_dns_returned(self, name, returned_dns, expected_out):
        ips = ["172-16-1-1", "172.16.1.1"]
        client = MagicMock()
        ip_rexp = compile(r"(([0-9]{1,3}[.-]){3}[0-9]{1,3})")
        backward_mismatch_file = MagicMock()
        forward_mismatch_file = MagicMock()
        backward_missing_file = MagicMock()

        with patch("dns_entry_checker.ssh_command"):
            dns_entry_checker.ssh_command.return_value = returned_dns

            check_ip_dns_mismatch(ips, client, ip_rexp, backward_mismatch_file, forward_mismatch_file,
                                  backward_missing_file)

        if not expected_out:
            backward_missing_file.write.assert_called_once()
        else:
            backward_missing_file.write.asser_not_called()

    @parameterized.expand(
        [
            ("Return doesn't contain IP", ["No IPS here"], 0),
            ("Returned IP doesn't match", ["test-host-172-16-1-2.nubes.stfc.ac.uk"], 1),
            ("Returned IP matches", ["test-host-172-16-1-1.nubes.stfc.ac.uk"], 2),
        ]
    )
    def test_check_ip_dns_mismatch_backwards_not_found(self, name, returned_ips, expected_out):
        ips = ["172-16-1-1", "172.16.1.1"]
        client = MagicMock()
        ip_rexp = compile(r"(([0-9]{1,3}[.-]){3}[0-9]{1,3})")
        backward_mismatch_file = MagicMock()
        forward_mismatch_file = MagicMock()
        backward_missing_file = MagicMock()

        with patch("dns_entry_checker.ssh_command"):
            dns_entry_checker.ssh_command.return_value = returned_ips

            check_ip_dns_mismatch(ips, client, ip_rexp, backward_mismatch_file, forward_mismatch_file,
                                  backward_missing_file)

        if expected_out == 0:
            backward_missing_file.write.assert_called_once()
        elif expected_out == 1:
            backward_mismatch_file.write.assert_called_once()
        else:
            backward_mismatch_file.write.assert_not_called()
            backward_missing_file.write.assert_not_called()

    @parameterized.expand(
        [
            ("Gaps", [5], True),
            ("No gaps", sorted(set(range(2, 255))), False),
        ]
    )
    def test_check_missing_ips(self, name, ips, expected_out):
        key = ("105", [str(x).zfill(0) for x in ips])
        gap_missing_file = MagicMock()
        i = 5

        check_missing_ips(key, gap_missing_file, i)

        if expected_out:
            gap_missing_file.write.assert_called()
        else:
            gap_missing_file.write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
