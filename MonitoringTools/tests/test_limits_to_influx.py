from unittest.mock import patch, call, NonCallableMock
from limits_to_influx import (
    convert_to_data_string,
    get_limit_prop_string,
    get_all_limits,
    main,
)
import pytest


def test_convert_to_data_string_no_items():
    """
    Tests convert_to_data_string returns empty string when given empty dict as limit_details
    """
    assert convert_to_data_string(NonCallableMock(), {}) == ""


@patch("limits_to_influx.get_limit_prop_string")
def test_convert_to_data_string_one_item(mock_get_limit_prop_string):
    """
    Tests convert_to_data_string works with single entry in dict for limit_details
    """
    mock_instance = "prod"
    mock_project_details = NonCallableMock()
    mock_limit_details = {"project foo": mock_project_details}
    mock_get_limit_prop_string.return_value = "prop1=val1"

    res = convert_to_data_string(mock_instance, mock_limit_details)
    assert res == 'Limits,Project="project\ foo",instance=Prod prop1=val1\n'
    mock_get_limit_prop_string.assert_called_once_with(mock_project_details)


@patch("limits_to_influx.get_limit_prop_string")
def test_convert_to_data_string_multi_item(mock_get_limit_prop_string):
    """
    Tests convert_to_data_string works with multiple entries in dict for limit_details
    """
    mock_instance = "prod"
    mock_project_details = NonCallableMock()

    mock_limit_details = {
        "project foo": mock_project_details,
        "project bar": mock_project_details,
    }
    mock_get_limit_prop_string.side_effect = ["prop1=val1", "prop1=val2"]
    assert (
        convert_to_data_string(mock_instance, mock_limit_details)
        == 'Limits,Project="project\ foo",instance=Prod prop1=val1\n'
        'Limits,Project="project\ bar",instance=Prod prop1=val2\n'
    )


@pytest.mark.parametrize(
    "details, expected",
    [
        ({}, ""),
        ({"key1": "123"}, "key1=123i"),
        (
            {"key1": "123", "key2": "456", "key3": "789"},
            "key1=123i,key2=456i,key3=789i",
        ),
    ],
)
def test_limit_prop_string(details, expected):
    """
    tests get_limit_prop_string converts dict into data string properly
    """
    assert get_limit_prop_string(details) == expected


def test_get_limits_for_project():
    # TODO: once we rewrite to using openstacksdk
    pass


@patch("limits_to_influx.openstack")
@patch("limits_to_influx.get_limits_for_project")
@patch("limits_to_influx.convert_to_data_string")
def test_get_all_limits(
    mock_convert_to_data_string, mock_get_limits_for_project, mock_openstack
):
    """
    tests get_all_limits function gets the limits of project appropriately
    """
    mock_project_list = [
        # to be ignored
        {"name": "xyz_rally", "id": "foo"},
        {"name": "844_xyz", "id": "bar"},
        # not to be ignored
        {"name": "proj1", "id": "proj1-id"},
        {"name": "proj2", "id": "proj2-id"},
    ]
    mock_conn_obj = mock_openstack.connect.return_value
    mock_conn_obj.list_projects.return_value = mock_project_list

    mock_instance = NonCallableMock()
    res = get_all_limits(mock_instance)
    mock_openstack.connect.assert_called_once_with(cloud=mock_instance)
    mock_conn_obj.list_projects.assert_called_once()
    mock_get_limits_for_project.assert_has_calls(
        [call(mock_instance, "proj1-id"), call(mock_instance, "proj2-id")]
    )

    mock_convert_to_data_string.assert_called_once_with(
        mock_instance,
        {
            "proj1": mock_get_limits_for_project.return_value,
            "proj2": mock_get_limits_for_project.return_value,
        },
    )
    assert res == mock_convert_to_data_string.return_value


@patch("limits_to_influx.run_scrape")
@patch("limits_to_influx.parse_args")
def test_main(mock_parse_args, mock_run_scrape):
    mock_user_args = NonCallableMock()
    main(mock_user_args)
    mock_run_scrape.assert_called_once_with(
        mock_parse_args.return_value, get_all_limits
    )
    mock_parse_args.assert_called_once_with(
        mock_user_args, description="Get All Project Limits"
    )
