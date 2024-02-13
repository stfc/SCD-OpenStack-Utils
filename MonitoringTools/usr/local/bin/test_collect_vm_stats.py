import unittest
from unittest.mock import NonCallableMock, Mock
from collect_vm_stats import (
    number_servers_active,
    number_servers_build,
    number_servers_error,
    number_servers_shutoff,
    number_servers_total,
    get_all_server_statuses,
    server_obj_to_len,
)


class TestVmStats(unittest.TestCase):

    def test_server_obj_to_len(self):
        """
        Tests that the length of a generator object is returned
        """
        mock_generator_obj = iter(
            [NonCallableMock(), NonCallableMock(), NonCallableMock()]
        )
        res = server_obj_to_len(mock_generator_obj)
        assert res == 3

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

    def test_get_all_server_statuses_raise_error(self):
        """
        Tests that if no cloud connection was given, a value error is raised
        """
        mock_cloud = None
        with self.assertRaises(ValueError):
            get_all_server_statuses(mock_cloud, prod=False)


if __name__ == "__main__":
    unittest.main()
