from unittest import mock
from unittest.mock import MagicMock, patch
from parameterized import parameterized
from datetime import datetime

import requests
import requests.auth
import word_cloud_generator
import unittest


class ChangingJson:
    """
    Class to represent a json object which changes value when it's called.
    """

    def __init__(self, values):
        """
        Constructs the attributes for the ChangingJson object
        :param values: The values for the ChangingJson to change through (list)
        """
        self.values = values
        self.current_index = 0

    def get(self, get_value):
        """
        Function to emulate the Json "Get" function while cycling through the values
        :param get_value: The value to requested (any)
        :return: The next value currently stored in the list (any)
        """
        return_value = self.values[self.current_index].get(get_value)
        if get_value == "size":
            self.current_index = (self.current_index + 1) % len(self.values)
        return return_value


auth = requests.auth.HTTPBasicAuth("test_username", "test_password")
headers = {
    "Accept": "application/json",
}
host = "https://test.com"


class WorldCloudGeneratorTests(unittest.TestCase):
    """
    Class for the test to be run against the functions from word_cloud_generator.py
    """

    @parameterized.expand(
        [
            ("check found", "something-else", True),
            ("check not found", b'{"status":"RUNNING"}', False),
        ]
    )
    def test_get_response_json(self, __, session_response_return_value, expected_out):
        """
        Function to test the functionality of get_response_json by asserting that the function
        calls a specific function or raises a Timeout error
        :param __: The name of the parameter, which is thrown away (string)
        :param session_response_return_value: The mocked return value for the
        session response (string)
        :param expected_out: The expected output of the function (bool)
        """
        with mock.patch("word_cloud_generator.requests") and patch(
            "word_cloud_generator.json"
        ):
            word_cloud_generator.requests.session = MagicMock()
            word_cloud_generator.requests.session.return_value.get.return_value.content = (
                session_response_return_value
            )

            word_cloud_generator.json = MagicMock()

            if expected_out:
                word_cloud_generator.get_response_json(auth, headers, host)

                word_cloud_generator.json.loads.assert_called_once()
            else:
                self.assertRaises(
                    requests.exceptions.Timeout,
                    word_cloud_generator.get_response_json,
                    auth,
                    headers,
                    host,
                )

    @parameterized.expand(
        [
            ("dates valid", "2022-01-01", ["test1", "test2", "test3", "test4"]),
            ("dates invalid", "2024-01-01", []),
        ]
    )
    def test_get_issues_contents_after_time(self, __, filter_date, expected_out):
        """
        Function to test the functionality of get_issues_contents_after_time by asserting
        that the value returned is expected
        :param __: The name of the parameter, which is thrown away (string)
        :param filter_date: The mocked date to filter after (list)
        :param expected_out: The expected output of the function (bool)
        """
        with mock.patch("word_cloud_generator.get_response_json"), mock.patch(
            "word_cloud_generator.filter_issue"
        ):
            issue_filter = {"end_date": filter_date}
            values = ChangingJson(
                (
                    {
                        "values": (
                            {
                                "fields": {
                                    "summary": "test1",
                                    "created": "2023-01-01T00:00:00",
                                }
                            },
                            {
                                "fields": {
                                    "summary": "test2",
                                    "created": "2023-01-01T00:00:00",
                                }
                            },
                        ),
                        "size": 50,
                    },
                    {
                        "values": (
                            {
                                "fields": {
                                    "summary": "test3",
                                    "created": "2023-01-01T00:00:00",
                                }
                            },
                            {
                                "fields": {
                                    "summary": "test4",
                                    "created": "2023-01-01T00:00:00",
                                }
                            },
                        ),
                        "size": 32,
                    },
                )
            )
            word_cloud_generator.get_response_json.return_value = values
            word_cloud_generator.filter_issue.return_value = True
            self.assertEqual(
                word_cloud_generator.get_issues_contents_after_time(
                    auth,
                    headers,
                    host,
                    issue_filter,
                ),
                expected_out,
            )

    @parameterized.expand(
        [
            ("dates valid", {"start_date": "2024-01-01", "assigned": "test"}, True),
            ("dates invalid", {"start_date": "2022-01-01", "assigned": "test"}, False),
            ("assigned valid", {"start_date": "2024-01-01", "assigned": "test"}, True),
            (
                "assigned invalid",
                {"start_date": "2024-01-01", "assigned": "test failed"},
                False,
            ),
        ]
    )
    def test_filter_issue(self, __, issue_filter, expected_out):
        """
        Function to test the functionality of filter_issue by asserting
        that the value returned is expected
        :param __: The name of the parameter, which is thrown away (string)
        :param issue_filter: The issue filter (dict)
        :param expected_out: The expected output of the function (bool)
        """
        issue = {"fields": {"assignee": {"displayName": "test"}}}
        issue_date = datetime.strptime("2023-01-01", "%Y-%m-%d")
        self.assertEqual(
            word_cloud_generator.filter_issue(
                issue,
                issue_filter,
                issue_date,
            ),
            expected_out,
        )

    def test_generate_word_cloud(self):
        """
        Function to test the functionality of generate_word_cloud by asserting that the function
        is called with specific inputs
        """
        with mock.patch("word_cloud_generator.filter_word_cloud"), mock.patch(
            "word_cloud_generator.WordCloud"
        ):
            issues_contents = "test data"
            issue_filter = ""
            word_cloud_output_location = "test"
            word_cloud_generator.generate_word_cloud(
                issues_contents,
                issue_filter,
                word_cloud_output_location,
            )
            word_cloud_generator.WordCloud.return_value.generate.assert_called_with(
                word_cloud_generator.filter_word_cloud.return_value
            )
            word_cloud_generator.WordCloud.return_value.to_file.assert_called_with(
                "test"
            )

    def test_filter_word_cloud(self):
        """
        Function to test the functionality of generate_word_cloud by asserting that the function
        returns an expected value
        """
        issue_filter = {
            "filter_not": "delete|this",
            "filter_for": "data|test|this|here|delete|not",
        }
        issues_contents = "test data delete this not here"
        self.assertEqual(
            word_cloud_generator.filter_word_cloud(issue_filter, issues_contents),
            "test data not here",
        )


if __name__ == "__main__":
    unittest.main()
