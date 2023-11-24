from unittest.mock import patch
from pynetboxquery.netbox_api.netbox_connect import api_object


@patch("pynetboxquery.netbox_api.netbox_connect.api")
def test_api_object(mock_api):
    """
    This test checks that the Api object is returned.
    """
    mock_url = "url"
    mock_token = "token"
    res = api_object(mock_url, mock_token)
    mock_api.assert_called_once_with(mock_url, mock_token)
    assert res == mock_api.return_value
