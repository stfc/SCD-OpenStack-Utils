from pathlib import Path
from unittest.mock import patch, ANY, NonCallableMock

import pytest

from builder.packer import (
    prepare_env,
    run_packer_build,
    get_packer_dir_from_repo_root,
    clear_output_directory,
    build_image,
    get_image_path,
)


def test_get_packer_dir_from_repo_root(tmp_path):
    """
    Test that the get_packer_dir_from_repo_root function returns the
    correct path.
    """
    repo_root = tmp_path / "repo_root"
    packer_dir = repo_root / "images" / "capi"

    assert get_packer_dir_from_repo_root(repo_root) == packer_dir


def test_prepare_env():
    """
    Test that the prepare_env function returns a dict with the
    PACKER_VAR_FILES key set to the correct path.
    """
    tmp_path = Path("/tmp")
    returned = prepare_env(tmp_path)

    assert "PACKER_VAR_FILES" in returned
    assert returned["PACKER_VAR_FILES"] == "/tmp/packer/config/stfc.json"


@patch("builder.packer.subprocess.Popen")
def test_run_packer(mock_popen):
    """
    Test that the run_packer function calls Popen with the correct
    arguments and waits for the process to finish.
    """
    proc = mock_popen.return_value.__enter__.return_value
    proc.returncode = 0

    tmp_path = Path("/tmp")
    expected_env = {"PACKER_VAR_FILES": "/tmp/packer/config/stfc.json"}

    with patch("builder.packer.prepare_env") as mock_prepare_env:
        mock_prepare_env.return_value = expected_env
        run_packer_build(tmp_path, "1234")

    mock_popen.assert_called_once_with(
        ["make", "build-qemu-ubuntu-1234"],
        cwd=tmp_path,
        env=expected_env,
        stdout=ANY,
        stderr=ANY,
        universal_newlines=True,
    )

    proc.wait.assert_called_once_with()


@patch("builder.packer.subprocess.Popen")
def test_run_packer_error(mock_popen):
    """
    Test that the run_packer function raises an exception if the
    process returns a non-zero exit code.
    """
    proc = mock_popen.return_value.__enter__.return_value
    proc.returncode = 1

    tmp_path = Path("/tmp")
    expected_env = {"PACKER_VAR_FILES": "/tmp/packer/config/stfc.json"}

    with patch("builder.packer.prepare_env") as mock_prepare_env:
        mock_prepare_env.return_value = expected_env
        with pytest.raises(RuntimeError):
            run_packer_build(tmp_path, "1234")

    mock_popen.assert_called_once_with(
        ["make", "build-qemu-ubuntu-1234"],
        cwd=tmp_path,
        env=expected_env,
        stdout=ANY,
        stderr=ANY,
        universal_newlines=True,
    )

    proc.wait.assert_called_once_with()


def test_clear_output_directory(tmp_path):
    """
    Test that the clear_output_directory function deletes all files
    from the output directory.
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    fake_ubuntu_paths = [
        output_dir / "ubuntu-2004-kube-v1.23.10",
        output_dir / "ubuntu-2004-kube-v1.24.99",
        output_dir / "other-arch",
    ]

    for path in fake_ubuntu_paths:
        path.mkdir()

    clear_output_directory(tmp_path)

    for path in fake_ubuntu_paths:
        assert not path.exists()
    assert not output_dir.exists()


def test_get_image_path(tmp_path):
    """
    Test that the get_image_path function returns the correct path.
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    output_subdir = output_dir / "ubuntu-2004-kube-v1.23.10"
    output_subdir.mkdir()

    output_file = output_subdir / "ubuntu-2004-kube-v1.23.10"
    with open(output_file, "wb") as file_handle:
        # 1GB file to pass the size check
        file_handle.truncate(1024 * 1024 * 1024)

    assert get_image_path(tmp_path) == output_file


def test_get_image_path_multiple_files(tmp_path):
    """
    Test that the get_image_path function raises an error if there
    are multiple files in the output directory.
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    output_subdir = output_dir / "ubuntu-2004-kube-v1.23.10"
    output_subdir.mkdir()

    (output_subdir / "ubuntu-2004-kube-v1.23.10").touch()
    (output_subdir / "extra-file").touch()

    with pytest.raises(RuntimeError) as error:
        get_image_path(tmp_path)

    assert "Expected exactly one file in the output directory." in str(error.value)


def test_get_image_path_small_file(tmp_path):
    """
    Test that the get_image_path function raises an error if the
    output file is less than 1GB.
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    output_subdir = output_dir / "ubuntu-2004-kube-v1.23.10"
    output_subdir.mkdir()

    output_file = output_subdir / "ubuntu-2004-kube-v1.23.10"
    with open(output_file, "wb") as file_handle:
        # 1GB - 1 byte file to fail the size check
        file_handle.truncate(1024 * 1024 * 1024 - 1)

    with pytest.raises(RuntimeError) as error:
        get_image_path(tmp_path)

    assert "Output file is less than 1GB. This is probably not an image." in str(
        error.value
    )


def test_build_image(tmp_path):
    """
    Test that the build_image function calls the correct functions in
    the correct order.
    """
    args = NonCallableMock()
    args.target_dir = tmp_path.as_posix()

    with patch(
        "builder.packer.get_packer_dir_from_repo_root"
    ) as mock_get_packer_dir_from_repo_root, patch(
        "builder.packer.clear_output_directory"
    ) as mock_clear_output_directory, patch(
        "builder.packer.run_packer_build"
    ) as mock_run_packer_build, patch(
        "builder.packer.get_image_path"
    ) as mock_get_image_path:
        returned = build_image(args)

    mock_get_packer_dir_from_repo_root.assert_called_once_with(tmp_path)
    packer_dir = mock_get_packer_dir_from_repo_root.return_value

    mock_clear_output_directory.assert_called_once_with(packer_dir)
    mock_run_packer_build.assert_called_once_with(packer_dir, args.os_version)
    mock_get_image_path.assert_called_once_with(packer_dir)

    assert returned == mock_get_image_path.return_value
