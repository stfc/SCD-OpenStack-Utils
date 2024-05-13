from src.get_github_prs import GetGitHubPRs, RepoNotFound, UnknownHTTPError
from unittest.mock import patch, call
import pytest


@pytest.fixture(scope="function", name="instance")
def instance_fixture():
    repo_list = ["repo1", "repo2"]
    return GetGitHubPRs(repo_list)


@patch("src.get_github_prs.GetGitHubPRs.format_http_responses")
@patch("src.get_github_prs.GetGitHubPRs.request_all_repos_http")
def test_run(mock_request, mock_format, instance):
    res = instance.run()
    mock_request.assert_called_once()
    mock_format.assert_called_once_with(mock_request.return_value)
    assert res == mock_format.return_value


@patch("src.get_github_prs.GetGitHubPRs.get_http_response")
def test_request_all_repos_http(mock_http, instance):
    mock_http.side_effect = ["response1", "response2"]
    res = instance.request_all_repos_http()
    mock_http.assert_has_calls(
        [
            call("https://api.github.com/repos/stfc/repo1/pulls"),
            call("https://api.github.com/repos/stfc/repo2/pulls"),
        ]
    )
    assert res == {
        "repo1": "response1",
        "repo2": "response2",
    }


@patch("src.get_github_prs.requests")
@patch("src.get_github_prs.get_token")
def test_get_http_response(mock_get_token, mock_requests, instance):
    mock_headers = {"Authorization": "token mock_token"}
    mock_get_token.return_value = "mock_token"
    res = instance.get_http_response("mock_url")
    mock_get_token.assert_called_once_with("GITHUB_TOKEN")
    mock_requests.get.assert_called_once_with(
        "mock_url", headers=mock_headers, timeout=60
    )
    assert res == mock_requests.get.return_value.json.return_value


def test_format_http_responses_valid(instance):
    mock_responses = {"repo1": [{"pr1": "data1"}, {"pr2": "data2"}, {"pr3": "data3"}]}
    res = instance.format_http_responses(mock_responses)
    assert res == mock_responses


def test_format_http_responses_no_open_prs(instance):
    mock_responses = {"repo1": []}
    res = instance.format_http_responses(mock_responses)
    assert res == {}


def test_format_http_responses_repo_not_found(instance):
    mock_responses = {"repo1": {"repo": "not_found", "docs": "here"}}
    with pytest.raises(RepoNotFound):
        res = instance.format_http_responses(mock_responses)
        assert not res


def test_format_http_responses_other_http_error(instance):
    mock_responses = {"repo1": "really strange error"}
    with pytest.raises(UnknownHTTPError):
        res = instance.format_http_responses(mock_responses)
        assert not res
