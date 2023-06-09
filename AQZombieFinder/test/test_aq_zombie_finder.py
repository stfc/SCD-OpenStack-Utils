import unittest
from unittest.mock import MagicMock, patch, NonCallableMock
from parameterized import parameterized

import aq_zombie_finder


class AQZombieFinderTests(unittest.TestCase):
    @patch("aq_zombie_finder.paramiko")
    def test_create_client(self, mock_paramiko):
        host = "test.aquilon.gridpp.rl.ac.uk"
        user = "test.abc12345"
        password = "test.A4gdfGs"

        mock_client = MagicMock()
        mock_paramiko.client.SSHClient.return_value = mock_client
        mock_paramiko.client.set_missing_host_key_policy = MagicMock()
        mock_paramiko.AutoAddPolicy = NonCallableMock()
        mock_paramiko.connect = MagicMock()

        client = aq_zombie_finder.create_client(host, user, password)

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

        command_output = aq_zombie_finder.ssh_command(mock_client, command)

        mock_client.exec_command.assert_called_once_with(
            command, get_pty=True, timeout=60
        )
        mock_stdout.channel.recv_exit_status.assert_called_once()
        mock_stdout.readlines.assert_called_once()

        self.assertEqual(command_output, mock_stdout.readlines.return_value)

    def test_get_aq_ips(self):
        openstack_client = MagicMock()

        mock_ip_addresses = "192.168.1.1"
        with patch("aq_zombie_finder.ssh_command"):
            aq_zombie_finder.ssh_command = MagicMock()
            aq_zombie_finder.ssh_command.return_value = ["Internal=192.168.1.1"]

            ip_addresses = aq_zombie_finder.get_aq_ips(openstack_client)

        self.assertEqual(ip_addresses[0][0], mock_ip_addresses)

    @parameterized.expand(
        [
            ("check not found", "Not Found:", False),
            ("check found", "something-else", "something-else"),
        ]
    )
    def test_check_openstack_ip(self, name, aq_host_return_value, expected_out):
        aq_ip = "test.192.168.1.1"
        aquilon_client = MagicMock()
        openstack_zombie_file = MagicMock()
        with patch("aq_zombie_finder.ssh_command"):
            aq_zombie_finder.ssh_command.return_value = aq_host_return_value

            host_output = aq_zombie_finder.check_openstack_ip(
                aq_ip, aquilon_client, openstack_zombie_file
            )

        self.assertEqual(host_output, expected_out)

    @parameterized.expand(
        [
            ("check not found", "No server with a name or ID of", False),
            ("check found", "Test", True),
        ]
    )
    def test_check_aquilon_serial(self, name, aq_host_return_value, expected_out):
        aq_host = r"Serial: test\\r"
        aq_ip = "test.192.168.1.1"
        aq_openstack_client = MagicMock()
        aquilon_zombie_file = MagicMock()

        aquilon_zombie_file.write = MagicMock()

        with patch("aq_zombie_finder.ssh_command"):
            aq_zombie_finder.ssh_command.return_value = aq_host_return_value

            aq_zombie_finder.check_aquilon_serial(
                aq_host, aq_ip, aq_openstack_client, aquilon_zombie_file
            )

        if expected_out:
            aquilon_zombie_file.assert_not_called()
        else:
            aquilon_zombie_file.write.assert_called_once()


if __name__ == "__main__":
    unittest.main()
