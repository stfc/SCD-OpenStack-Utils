from src.post_to_influx import PostDataToInflux
from unittest.mock import patch
import pytest


@pytest.fixture(scope="function", name="instance")
def instance_fixture():
    """This fixture returns the module class."""
    with patch("src.post_to_influx.get_token"):
        return PostDataToInflux()


@patch("src.post_to_influx.get_repos")
@patch("src.post_to_influx.GetGitHubPRs")
@patch("src.post_to_influx.PostDataToInflux.create_data_points")
@patch("src.post_to_influx.PostDataToInflux.write_to_influx")
def test_run(mock_write, mock_create, mock_github, mock_repos, instance):
    """This test checks that all the correct functions are called and none are missed."""
    mock_repos.return_value = ["mock_pr"]
    instance.run()
    mock_github.assert_called_once_with(["mock_pr"])
    mock_github.return_value.run.assert_called_once()
    mock_create.assert_called_once_with(mock_github.return_value.run.return_value)
    mock_write.assert_called_once_with(mock_create.return_value)
