import unittest
from unittest import mock
from unittest.mock import NonCallableMock, Mock

import vm_stats
from vm_stats import (
    number_servers_active,
    number_servers_build,
    number_servers_error,
    number_servers_shutoff,
    number_servers_total,
    collect_stats,
)


class TestVmStats(unittest.TestCase):

    def test_number_servers_total(self):
        """
        Tests that the total number of servers can be queried and counted
        """
        mock_conn = Mock()
        mock_server_results = iter(
            [NonCallableMock(), NonCallableMock(), NonCallableMock()]
        )
        mock_conn.compute.servers.return_value = mock_server_results
        num_returned = number_servers_total(mock_conn)
        assert num_returned == 3

    def test_number_servers_active(self):
        """
        Tests that the active servers can be queried and counted
        """
        mock_conn = Mock()
        mock_server_results = iter(
            [NonCallableMock(), NonCallableMock(), NonCallableMock()]
        )
        mock_conn.compute.servers.return_value = mock_server_results
        num_returned = number_servers_active(mock_conn)
        assert num_returned == 3

    def test_number_servers_build(self):
        """
        Tests that the servers in build state can be queried and counted
        """
        mock_conn = Mock()
        mock_server_results = iter(
            [NonCallableMock(), NonCallableMock(), NonCallableMock()]
        )
        mock_conn.compute.servers.return_value = mock_server_results
        num_returned = number_servers_build(mock_conn)
        assert num_returned == 3

    def test_number_servers_error(self):
        """
        Tests that the error servers can be queried and counted
        """
        mock_conn = Mock()
        mock_server_results = iter(
            [NonCallableMock(), NonCallableMock(), NonCallableMock()]
        )
        mock_conn.compute.servers.return_value = mock_server_results
        num_returned = number_servers_error(mock_conn)
        assert num_returned == 3

    def test_number_servers_shutoff(self):
        """
        Tests that the shutoff servers can be queried and counted
        """
        mock_conn = Mock()
        mock_server_results = iter(
            [NonCallableMock(), NonCallableMock(), NonCallableMock()]
        )
        mock_conn.compute.servers.return_value = mock_server_results
        num_returned = number_servers_shutoff(mock_conn)
        assert num_returned == 3

    # WIP Unit Test
    def test_collect_stats(self):
        """
        Test that stats are collected and stats methods are called
        """
        mock_cloud_conn = Mock()

        mock_vm_stats = {
            "total_vms": NonCallableMock(),
            "active_vms": NonCallableMock(),
            "build_vms": NonCallableMock(),
            "error_vms": NonCallableMock(),
            "shutoff_vms": NonCallableMock(),
        }


if __name__ == "__main__":
    unittest.main()
