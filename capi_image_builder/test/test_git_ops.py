from pathlib import Path
from unittest import mock
from unittest.mock import patch

import pytest
from git import GitCommandError

from builder.git_ops import GitOps

FORK_URL = "https://github.com/stfc/k8s-image-builder.git"
UPSTREAM_URL = "https://github.com/kubernetes-sigs/image-builder.git"


def test_git_clone_validates_protocol_ssh():
    with pytest.raises(ValueError):
        GitOps(ssh_key_path=Path("/tmp/id_rsa")).git_clone(
            "https://example.com", "/tmp/target"
        )


@patch("builder.git_ops.Repo.clone_from")
def test_git_clone_ssh(clone):
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
    ops = GitOps(ssh_key_path=Path("/tmp/id_rsa"))
    ops.repo = mock.Mock()

    mock_username = mock.NonCallableMock()
    ops.set_git_username(mock_username)
    ops.repo.config_writer().set_value.assert_called_once_with(
        "user", "name", mock_username
    )
    ops.repo.config_writer().set_value().release.assert_called_once()


def test_git_set_email():
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
    path = tmp_path_factory.mktemp("git_env")
    ops = GitOps(ssh_key_path=Path("/tmp/id_rsa"))

    # Patch out validation, so we can use https
    # rather than mess with keys
    with patch("builder.git_ops.GitOps._validate_protocol"):
        ops.git_clone(FORK_URL, path)
    return ops


def test_git_upstream_add():
    ops = GitOps(ssh_key_path=Path("/tmp/id_rsa"))
    ops.repo = mock.MagicMock()

    ops.git_add_upstream(UPSTREAM_URL, remote_name="upstream_add")
    ops.repo.create_remote.assert_called_once_with("upstream_add", UPSTREAM_URL)


def test_git_fetch_upstream_mock():
    ops = GitOps(ssh_key_path=Path("/tmp/id_rsa"))
    # Patch fetch to not actually fetch
    ops.repo = mock.MagicMock()

    ops.git_fetch_upstream("upstream_fetch")
    ops.repo.remotes["upstream_fetch"].fetch.assert_called_once_with()


def test_git_rebase_mock():
    ops = GitOps(ssh_key_path=Path("/tmp/id_rsa"))
    # Patch rebase to not actually rebase
    ops.repo = mock.MagicMock()

    ops.git_rebase_upstream("upstream_rebase", "master")
    ops.repo.git.rebase.assert_called_once_with("upstream_rebase/master")


def test_git_rebase_real(_prepared_repo):
    _prepared_repo.git_add_upstream(UPSTREAM_URL)
    assert "upstream" in _prepared_repo.repo.remotes

    # Manually checkout to a known starting commit to rebase from
    _prepared_repo.repo.git.checkout("8e2d88942e66afc89aeb21e5e27e562f184fc08d")

    # dfbd4fc1dbb2ee1808b17a8fb4d0a5b03417fb5a
    # is the next merge commit upstream, so this should be
    # present after the rebase
    with pytest.raises(GitCommandError):
        _prepared_repo.repo.git.branch(
            "--contains", "dfbd4fc1dbb2ee1808b17a8fb4d0a5b03417fb5a"
        )

    _prepared_repo.set_git_username("ci-test")
    _prepared_repo.set_git_email("test@example.com")

    _prepared_repo.git_fetch_upstream()
    _prepared_repo.git_rebase_upstream()

    assert _prepared_repo.repo.git.branch(
        "--contains", "dfbd4fc1dbb2ee1808b17a8fb4d0a5b03417fb5a"
    )
