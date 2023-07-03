import unittest
from unittest.mock import patch, NonCallableMock
import vm_creation_v2


class VmCreationTests(unittest.TestCase):
    @patch.object(vm_creation_v2, "conn")
    def test_get_image(self, mocked_conn):
        # empty list check
        expected_value = []
        mocked_conn.image.images.return_value = []
        res = vm_creation_v2.get_image()
        mocked_conn.image.images.assert_called_once()
        self.assertEqual(res, expected_value)

    def test_select_single_image(self):
        mock_image = NonCallableMock()
        mock_image.status = "active"
        mock_image_list = [mock_image]
        res = vm_creation_v2.select_single_image(mock_image_list)
        self.assertEqual(mock_image, res)

    @patch.object(vm_creation_v2, "conn")
    def test_get_flavors(self, mocked_conn):
        # empty list check
        expected_value = []
        mocked_conn.compute.flavors.return_value = []
        res = vm_creation_v2.get_flavors()
        mocked_conn.compute.flavors.assert_called_once_with(get_extra_specs=True)
        self.assertEqual(res, expected_value)

    @patch("vm_creation_v2.get_flavors")
    def test_find_flavors_with_hosttype(self, mocked_get_flavor):
        # mock a value which will pass the test
        mock_extra_specs_true = NonCallableMock()
        mock_extra_specs_true.extra_specs = ["aggregate_instance_extra_specs:hosttype"]
        # mock a value which doesn't pass
        mock_extra_specs_false = NonCallableMock()
        mock_extra_specs_false.extra_specs = []
        # run test
        mocked_get_flavor.return_value = [mock_extra_specs_false, mock_extra_specs_true]
        res = vm_creation_v2.find_flavors_with_hosttype()
        self.assertEqual(res, [mock_extra_specs_true])

    @patch.object(vm_creation_v2, "conn")
    def test_get_aggregates(self, mocked_conn):
        # empty list check
        expected_value = []
        mocked_conn.compute.aggregates.return_value = []
        res = vm_creation_v2.get_aggregates()
        mocked_conn.compute.aggregates.assert_called_once_with(get_extra_specs=True)
        self.assertEqual(res, expected_value)

    @patch("vm_creation_v2.get_aggregates")
    def test_find_aggregates_with_hosttype(self, mocked_get_aggregates):
        # mock a value which will pass the test
        mock_metadata_true = NonCallableMock()
        mock_metadata_true.metadata = ["hosttype"]
        # mock a value which doesn't pass
        mock_metadata_false = NonCallableMock()
        mock_metadata_false.metadata = []
        # run test
        mocked_get_aggregates.return_value = [mock_metadata_false, mock_metadata_true]
        res = vm_creation_v2.find_aggregates_with_hosttype()
        self.assertEqual(res, [mock_metadata_true])

    def test_find_smallest_flavor_different_hosttype(self):
        mock_flavor1 = {
            "ram": 10,
            "extra_specs": {"aggregate_instance_extra_specs:hosttype": "test_type1"},
        }
        mock_flavor2 = {
            "ram": 11,
            "extra_specs": {"aggregate_instance_extra_specs:hosttype": "test_type2"},
        }
        mock_input = [mock_flavor1, mock_flavor2]
        res = vm_creation_v2.find_smallest_flavors(mock_input)
        self.assertEqual({"test_type1": mock_flavor1, "test_type2": mock_flavor2}, res)

    def test_find_smallest_flavor_same_hosttype(self):
        mock_flavor1 = {
            "ram": 10,
            "extra_specs": {"aggregate_instance_extra_specs:hosttype": "test_type1"},
        }

        mock_flavor2 = {
            "ram": 11,
            "extra_specs": {"aggregate_instance_extra_specs:hosttype": "test_type1"},
        }

        mock_input = [mock_flavor1, mock_flavor2]
        res = vm_creation_v2.find_smallest_flavors(mock_input)
        self.assertEqual({"test_type1": mock_flavor1}, res)

    def test_find_smallest_flavor_for_each_aggregate(self):
        mock_flavor = {
            "extra_specs": {"aggregate_instance_extra_specs:hosttype": "test_type1"}
        }
        mock_aggregate = {
            "metadata": {"hosttype": "test_type1"},
            "name": "mock_aggregate",
        }
        mock_flavors_input = {"flavor1": mock_flavor}
        mock_aggregates_input = [mock_aggregate]
        res = vm_creation_v2.find_smallest_flavor_for_each_aggregate(
            mock_flavors_input, mock_aggregates_input
        )
        self.assertEqual({"mock_aggregate": mock_flavor}, res)

    def test_create_dictionary_of_aggregates_to_hostname(self):
        mock_aggregate = {"name": "aggregate1", "hosts": ["host1, host2, host3"]}
        mock_aggregate_input = [mock_aggregate]
        res = vm_creation_v2.create_dictionary_of_aggregates_to_hostnames(
            mock_aggregate_input
        )
        self.assertEqual({"aggregate1": ["host1, host2, host3"]}, res)

    def test_remove_values(self):
        aggregate = NonCallableMock()
        mock_hv1 = NonCallableMock()
        mock_hv1.status = "enabled"
        mock_hv2 = NonCallableMock()
        mock_hv2.status = "disabled"
        mock_dictionary = {aggregate: [mock_hv1, mock_hv2]}
        res = vm_creation_v2.remove_values(mock_dictionary)
        self.assertEqual({aggregate: [mock_hv1]}, res)

    @patch.object(vm_creation_v2, "conn")
    def test_list_all_hv_objects(self, mocked_conn):
        # empty list check
        expected_value = []
        mocked_conn.compute.hypervisors.return_value = []
        res = vm_creation_v2.list_all_hv_objects()
        mocked_conn.compute.hypervisors.assert_called_once_with(details=True)
        self.assertEqual(res, expected_value)

    def test_create_dict_of_aggregate_to_hv_objects(self):
        mocked_hv1 = NonCallableMock()
        mocked_hv1.name = "host1"
        mock_hv_list = [mocked_hv1]
        mocked_aggregate_to_hvs_list = {"aggregate1": ["host1"]}
        res = vm_creation_v2.create_dict_of_aggregate_to_hv_objects(
            mocked_aggregate_to_hvs_list, mock_hv_list
        )
        self.assertEqual({"aggregate1": [mocked_hv1]}, res)

    def test_recontextualise_hvs(self):
        mock_flavor1 = NonCallableMock()
        mock_aggregate_flavor_dict = {"aggregate1": mock_flavor1}
        mock_hv1 = NonCallableMock()
        mock_aggregate_hvs_dict = {"aggregate1": [mock_hv1]}
        res = vm_creation_v2.recontextualise_hvs(
            mock_aggregate_flavor_dict, mock_aggregate_hvs_dict
        )
        self.assertEqual({"aggregate1": [mock_hv1]}, res)

    def test_create_vms_on_hvs_with_space(self):
        mock_image = NonCallableMock()
        mock_image.id = "2"
        mock_flavor1 = NonCallableMock()
        mock_flavor1.ram = 5
        mock_flavor1.vcpus = 4
        mock_flavor1.name = "test_flav"
        mock_aggregate_flavor_dict = {"aggregate1": mock_flavor1}
        mock_hv1 = NonCallableMock()
        mock_hv1.memory_free = 20
        mock_hv1.vcpus = 20
        mock_hv1.vcpus_used = 4
        mock_hv1.name = "Test"
        mock_hv_list = {"aggregate1": [mock_hv1]}
        res = vm_creation_v2.create_vms_on_hvs_with_space(
            mock_hv_list, mock_aggregate_flavor_dict, mock_image
        )
        self.assertEqual([f"A VM has been created on {mock_hv1.name}"], res)


if __name__ == "__main__":
    unittest.main()
