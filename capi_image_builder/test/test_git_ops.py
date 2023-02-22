from pathlib import Path
from unittest import mock
from unittest.mock import patch, NonCallableMock

import pytest
from git import GitCommandError

from builder.git_ops import GitOps

FORK_URL = "https://github.com/stfc/k8s-image-builder.git"
UPSTREAM_URL = "https://github.com/kubernetes-sigs/image-builder.git"


def test_git_clone_validates_protocol_ssh():
    """
    Test that the git clone method validates the protocol is
    only SSH, so that we can later push to the repo.
    """
    with pytest.raises(ValueError):
        GitOps(ssh_key_path=Path("/tmp/id_rsa")).git_clone(
            "https://example.com", Path("/tmp/target")
        )


@patch("builder.git_ops.Repo.clone_from")
def test_git_clone_ssh(clone):
    """
    Test that the git clone method is called with the correct
    arguments.
    """
    keypair_mock = mock.NonCallableMock()
    expected_url = mock.NonCallableMock()
    expected_dir = mock.NonCallableMock()
    repo = GitOps(ssh_key_path=keypair_mock).git_clone(expected_url, expected_dir)

    assert repo is clone.return_value

    clone.assert_called_once_with(
        expected_url,
        expected_dir,
        env={"GIT_SSH_COMMAND": f"ssh -i {keypair_mock}"},
    )


def test_git_set_username():
    """
    Test that the git username is set correctly.
    """
    ops = GitOps(ssh_key_path=Path("/tmp/id_rsa"))
    ops.repo = mock.Mock()

    mock_username = mock.NonCallableMock()
    ops.set_git_username(mock_username)
    ops.repo.config_writer().set_value.assert_called_once_with(
        "user", "name", mock_username
    )
    ops.repo.config_writer().set_value().release.assert_called_once()


def test_git_set_email():
    """
    Test that the git email is set correctly.
    """
    ops = GitOps(ssh_key_path=Path("/tmp/id_rsa"))
    ops.repo = mock.Mock()

    mock_email = mock.NonCallableMock()
    ops.set_git_email(mock_email)
    ops.repo.config_writer().set_value.assert_called_once_with(
        "user", "email", mock_email
    )
    ops.repo.config_writer().set_value().release.assert_called_once()


@pytest.fixture(scope="session")
def _prepared_repo(tmp_path_factory) -> GitOps:
    """
    Fixture to return a pre-cloned repo for testing.
    """
    path = tmp_path_factory.mktemp("git_env")
    ops = GitOps(ssh_key_path=Path("/tmp/id_rsa"))

    # Patch out validation, so we can use https
    # rather than mess with keys
    with patch("builder.git_ops.GitOps._validate_protocol"):
        ops.git_clone(FORK_URL, path)
    return ops


def test_git_upstream_add():
    """
    Tests that the correct upstream repo is added.
    """
    ops = GitOps(ssh_key_path=Path("/tmp/id_rsa"))
    ops.repo = mock.MagicMock()

    ops.git_add_upstream(UPSTREAM_URL, remote_name="upstream_add")
    ops.repo.create_remote.assert_called_once_with("upstream_add", UPSTREAM_URL)


def test_git_fetch_upstream_mock():
    """
    Tests that the fetch upstream method is called correctly.
    """
    ops = GitOps(ssh_key_path=Path("/tmp/id_rsa"))
    # Patch fetch to not actually fetch
    ops.repo = mock.MagicMock()

    ops.git_fetch_upstream("upstream_fetch")
    ops.repo.remotes["upstream_fetch"].fetch.assert_called_once_with()


def test_git_merge_mock():
    """
    Tests that the merge upstream method is called correctly.
    """
    ops = GitOps(ssh_key_path=Path("/tmp/id_rsa"))
    # Patch rebase to not actually rebase
    ops.repo = mock.MagicMock()

    ops.git_merge_upstream("upstream_rebase", "master")
    ops.repo.git.merge.assert_called_once_with("upstream_rebase/master")


def test_git_push_mock():
    """
    Tests that the push upstream method is called correctly.
    """
    ops = GitOps(ssh_key_path=Path("/tmp/id_rsa"))
    # Patch push to not actually push
    ops.repo = mock.MagicMock()

    remote, branch = NonCallableMock(), NonCallableMock()

    ops.git_push(remote, branch)
    ops.repo.git.push.assert_called_once_with(remote, branch)
