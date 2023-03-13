from pathlib import Path
from unittest.mock import patch, Mock, create_autospec, NonCallableMock, call

from git import Repo

from args import Args
from builder.git_ops import GitOps
from builder.git_steps import (
    populate_temp_dir,
    clone_repo,
    K8S_FORK_URL,
    update_repo,
    UPSTREAM_URL,
    prepare_image_repo,
    checkout_branch,
)


def test_new_temp_directory_generated():
    """
    Test that a new temporary directory is generated if one is not provided.
    """
    args = Args(
        target_dir=None, ssh_key_path="test", push_to_github=False, openstack_cloud=""
    )
    args = populate_temp_dir(args)

    assert args.target_dir is not None
    assert args.is_tmp_dir
    Path(args.target_dir).exists()


def test_existing_path_not_overwritten(tmp_path):
    """
    Test that an existing path is not overwritten and the
    destination directory is created.
    """
    expected_dir = tmp_path / "existing_path"
    args = Args(
        target_dir=expected_dir.as_posix(),
        ssh_key_path="test",
        push_to_github=False,
        openstack_cloud="",
    )

    assert not expected_dir.exists()
    args = populate_temp_dir(args)
    assert not args.is_tmp_dir
    assert args.target_dir == expected_dir.as_posix()
    assert expected_dir.exists()


@patch("builder.git_steps.GitOps")
@patch("builder.git_steps.Path")
def test_clone_repo(path_mock, git_ops):
    """
    Test that the repo is cloned to the target directory.
    """
    args = Mock()

    with patch("builder.git_steps.populate_temp_dir") as populate_mock:
        returned = clone_repo(args)
        populate_mock.assert_called_once_with(args)
        updated_args = populate_mock.return_value

    assert returned == git_ops.return_value
    git_ops.assert_called_once_with(path_mock.return_value)
    ops_class = git_ops.return_value

    # Clone
    ops_class.git_clone.assert_called_once_with(K8S_FORK_URL, path_mock.return_value)

    path_mock.assert_has_calls(
        [call(updated_args.ssh_key_path), call(updated_args.target_dir)]
    )


def test_checkout_branch():
    """
    Test that the branch is checked out.
    """
    branch = "test"
    ops = create_autospec(GitOps)
    ops.repo = create_autospec(Repo)
    checkout_branch(ops, branch)
    ops.repo.git.checkout.assert_called_once_with(branch)


def test_update_repo():
    """
    Test that the repo is updated with the upstream fork.
    """
    ops = create_autospec(GitOps)
    update_repo(ops, push=False)
    ops.git_add_upstream.assert_called_once_with(UPSTREAM_URL)
    ops.git_fetch_upstream.assert_called_once_with()
    ops.git_merge_upstream.assert_called_once_with()

    # These should be pre-set on the system
    ops.set_git_username.assert_not_called()
    ops.set_git_email.assert_not_called()


@patch("builder.git_steps.clone_repo")
@patch("builder.git_steps.checkout_branch")
@patch("builder.git_steps.update_repo")
def test_prepare_image_repo(update_mock, checkout_mock, clone_mock):
    """
    Test that the repo is cloned and merged as expected
    """
    arg_mock = NonCallableMock()
    prepare_image_repo(arg_mock)

    clone_mock.assert_called_once_with(arg_mock)
    checkout_mock.assert_called_once_with(clone_mock.return_value, arg_mock.git_branch)
    update_mock.assert_called_once_with(
        clone_mock.return_value, arg_mock.push_to_github
    )


def test_git_push_disabled():
    """
    Test that the repo is not pushed to the remote if the push flag is not set.
    """
    ops = create_autospec(GitOps)
    update_repo(ops, push=False)
    ops.git_push.assert_not_called()


def test_git_push_enabled():
    """
    Test that the repo is pushed to the remote if the push flag is set.
    """
    ops = create_autospec(GitOps)
    update_repo(ops, push=True)
    ops.git_push.assert_called_once_with()
