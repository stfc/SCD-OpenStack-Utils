from unittest import mock
from unittest.mock import MagicMock, patch, call
from parameterized import parameterized

import requests
import requests.auth
import jsm_metric_collection
import unittest

auth = requests.auth.HTTPBasicAuth("test_username", "test_password")
headers = {
    "Accept": "application/json",
}
host = "https://test.com"
titles = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)


class ChangingJson:
    def __init__(self, values):
        self.values = values
        self.current_index = 0

    def get_next_value(self):
        value = self.values[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.values)
        return value

    def get(self, get_value):
        return self.get_next_value().get(get_value)


class JSMMetricCollectionTests(unittest.TestCase):
    @parameterized.expand(
        [
            ("check found", "something-else", True),
            ("check not found", b'{"status":"RUNNING"}', False),
        ]
    )
    def test_get_response_json(self, __, session_response_return_value, expected_out):

        with mock.patch("jsm_metric_collection.requests") and patch("jsm_metric_collection.json"):
            jsm_metric_collection.requests.session = MagicMock()
            jsm_metric_collection.requests.session.return_value.get.return_value.content = session_response_return_value

            jsm_metric_collection.json = MagicMock()

            if expected_out:
                jsm_metric_collection.get_response_json(auth, headers, host)

                jsm_metric_collection.json.loads.assert_called_once()
            else:
                self.assertRaises(requests.exceptions.Timeout, jsm_metric_collection.get_response_json,
                                  auth, headers, host)

    def test_get_report_task_id(self):
        query = "test?timescaleId=2"

        with mock.patch("jsm_metric_collection.get_response_json"):
            jsm_metric_collection.get_response_json.return_value = {"taskId": "10000"}

            self.assertEqual(jsm_metric_collection.get_report_task_id(auth, headers, host, query), "10000")

    def test_get_issues_amount(self):
        with mock.patch("jsm_metric_collection.get_response_json"):
            values = ChangingJson([{"size": 50}, {"size": 32}])
            jsm_metric_collection.get_response_json.return_value = values
            self.assertEqual(jsm_metric_collection.get_issues_amount(auth, headers, host), [82])

    def test_get_report_values(self):
        job_id = "10000"

        with mock.patch("jsm_metric_collection.get_response_json"):
            jsm_metric_collection.get_response_json.return_value = {
                "reportDataResponse": {
                    "series": (
                        {"seriesSummaryValue": 10}, {"seriesSummaryValue": 20})}}
            self.assertEqual(jsm_metric_collection.get_report_values(auth, headers, host, job_id), [10, 20])

    def test_get_customer_satisfaction(self):
        time_series = 4

        with mock.patch("jsm_metric_collection.get_response_json"):
            jsm_metric_collection.get_response_json.return_value = {
                "summary": {
                    "average": 5, "count": 5
                }}

            self.assertEqual(jsm_metric_collection.get_customer_satisfaction(auth, headers, host, time_series), [5, 5])

    @parameterized.expand(
        [
            ("check if exists", 1),
            ("check if not exists", 0),
        ]
    )
    @mock.patch("builtins.open")
    def test_save_csv(self, __, csv_data, expected_out):
        jsm_data = [[csv_data]]
        csv_output_location = "output/JSM Metric Data.csv"

        with mock.patch("csv.reader") as csv_reader:
            csv_reader.return_value = [[[1]]]

            jsm_metric_collection.save_csv(jsm_data, csv_output_location)

            if expected_out:
                assert call("csv_output_location", "a+", "newline=") not in csv_reader.mock_calls
            else:
                assert call("csv_output_location", "a+", "newline=") in csv_reader.mock_calls

    @mock.patch("builtins.open")
    def test_generate_xlsx_file(self, __):
        csv_output_location = "output/JSM Metric Data.csv"
        xlsx_output_location = "output/JSM Metric Data.csv"

        with mock.patch("xlsxwriter.Workbook"):
            jsm_metric_collection.generate_jsm_data_page = MagicMock()
            jsm_metric_collection.generate_jsm_graph_page = MagicMock()

            jsm_metric_collection.generate_xlsx_file(csv_output_location, xlsx_output_location)

            jsm_metric_collection.generate_jsm_data_page.assert_called_once()
            jsm_metric_collection.generate_jsm_graph_page.assert_called_once()

    def test_generate_jsm_data_page(self):
        workbook = MagicMock()
        jsm_data = [["test data"]]

        workbook.add_format.return_value = "test_format"

        jsm_metric_collection.generate_jsm_data_page(workbook, jsm_data, titles)

        workbook.add_worksheet.return_value.add_table.assert_called_once_with(
            "A1:L2", {
                "data": [["test data"]],
                "style": "Table Style Light 15",
                "columns": [
                    {"header": 0, "format": "test_format"},
                    {"header": 1},
                    {"header": 2},
                    {"header": 3},
                    {"header": 4, 'format': "test_format"},
                    {"header": 5},
                    {"header": 6},
                    {"header": 7},
                    {"header": 8},
                    {"header": 9, "format": "test_format"},
                    {"header": 10},
                    {"header": 11}
                ]
            }
        )

    def test_generate_jsm_graph_page(self):
        workbook = MagicMock()
        jsm_data = [["test data"]]

        jsm_metric_collection.generate_jsm_graph_page(workbook, jsm_data, titles)

        workbook.add_worksheet.return_value.insert_chart.assert_called_with("J50", workbook.add_chart())


if __name__ == "__main__":
    unittest.main()
