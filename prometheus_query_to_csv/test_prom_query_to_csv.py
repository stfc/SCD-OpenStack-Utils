from unittest.mock import patch, NonCallableMock
import pytest
from prom_query_to_csv import RawData, JsonToCSV


@pytest.fixture(name="instance_raw_data")
def instance_raw_data_fixture():
    """
    This fixture returns an instance of the RawData class.
    """
    mock_metrics = ["metric1", "metric2"]
    mock_start = "123"
    mock_end = "456"
    mock_url = "http://mock.url.com"
    return RawData(mock_metrics, mock_start, mock_end, mock_url)


@pytest.fixture(name="instance_json_to_csv")
def instance_json_to_csv_fixture():
    """
    This fixture returns an isntance of the JsonToCSV class.
    """
    mock_metrics = ["metric1", "metric2"]
    return JsonToCSV(mock_metrics)


@patch("prom_query_to_csv.RawData.http_request")
@patch("prom_query_to_csv.RawData.write_json_file")
def test_request_to_json_file(
    mock_write_json_file, mock_http_request, instance_raw_data
):
    """
    This test makes sure both methods involved are called correctly.
    """
    mock_http_request.return_value = "mock_http_return"
    res = instance_raw_data.request_to_json_file()
    mock_http_request.assert_any_call(
        {
            "query": "metric2",
            "start": "123",
            "end": "456",
            "step": 60,
        }
    )
    mock_http_request.assert_any_call(
        {
            "query": "metric1",
            "start": "123",
            "end": "456",
            "step": 60,
        }
    )
    mock_write_json_file.assert_any_call("metric1", "mock_http_return")
    mock_write_json_file.assert_any_call("metric2", "mock_http_return")
    assert not res


@patch("prom_query_to_csv.requests.get")
def test_http_request(mock_get, instance_raw_data):
    """
    This test ensures the requests.get method is called with the correct parameters.
    """
    res = instance_raw_data.http_request("mock_metric")
    mock_get.assert_called_once_with(
        "http://mock.url.com", params="mock_metric", timeout=300
    )
    assert res == mock_get.return_value


@patch("prom_query_to_csv.open")
def test_write_json_file(mock_open, instance_raw_data):
    """
    This test ensures the open method is called and the data should be written.
    """
    mock_response = NonCallableMock()
    mock_response.json.return_value = "mock_data"
    res = instance_raw_data.write_json_file("mock_name", mock_response)
    mock_open.assert_called_once_with("mock_name.csv", "w", encoding="utf-8")
    mock_response.json.assert_called_once()
    mock_open.return_value.__enter__.return_value.write.assert_called_once_with(
        "mock_data"
    )
    assert not res


@patch("prom_query_to_csv.JsonToCSV.dict_to_csv")
@patch("prom_query_to_csv.JsonToCSV.json_to_dict")
@patch("prom_query_to_csv.JsonToCSV.read_json")
def test_json_to_csv(
    mock_read_json, mock_json_to_dict, mock_dict_to_csv, instance_json_to_csv
):
    """
    This test checks that the read methods are called.
    """
    mock_read_json.return_value = "mock_data"
    res = instance_json_to_csv.json_to_csv()
    mock_read_json.assert_any_call("metric1")
    mock_read_json.assert_any_call("metric2")
    mock_json_to_dict.assert_any_call("mock_data")
    mock_dict_to_csv.assert_any_call(mock_json_to_dict.return_value)
    assert not res


@patch("prom_query_to_csv.open")
def test_read_json(mock_open, instance_json_to_csv):
    """
    This test is testing that the open is called correctly.
    """
    res = instance_json_to_csv.read_json("mock_file")
    mock_open.assert_called_once_with("mock_file.csv", "r", encoding="utf-8")
    mock_open.return_value.__enter__.return_value.read.assert_called_once()
    assert res == mock_open.return_value.__enter__.return_value.read.return_value


def test_json_to_dict(instance_json_to_csv):
    """
    This test is ensuring that json loads reads the data in correctly
    """
    mock_data = '{"mock_key":"mock_value"}'
    res = instance_json_to_csv.json_to_dict(mock_data)
    assert res == {"mock_key": "mock_value"}


@patch("prom_query_to_csv.JsonToCSV.dict_to_csv_openstack")
def test_dict_to_csv_openstack(mock_openstack, instance_json_to_csv):
    """
        This calls the openstack handling method when a openstack metric is found
        """
    mock_data = {"data": {"result": [{"metric": {"__name__": "openstack"}}]}}
    res = instance_json_to_csv.dict_to_csv(mock_data)
    mock_openstack.assert_called_once_with(mock_data["data"]["result"])
    assert not res


@patch("prom_query_to_csv.JsonToCSV.dict_to_csv_node")
def test_dict_to_csv_node(mock_node, instance_json_to_csv):
    """
    This calls the node handling method when a node metric is found
    """
    mock_data = {"data": {"result": [{"metric": {"__name__": "node"}}]}}
    res = instance_json_to_csv.dict_to_csv(mock_data)
    mock_node.assert_called_once_with(mock_data["data"]["result"])
    assert not res


def test_dict_to_csv_neither(instance_json_to_csv):
    """
    This test case ensures an error is raised when a metric is found that is neither of the supported metrics.
    """
    mock_data = {"data": {"result": [{"metric": {"__name__": "error"}}]}}
    with pytest.raises(Exception):
        res = instance_json_to_csv.dict_to_csv(mock_data)
        assert not res
