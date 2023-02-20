from pathlib import Path
from unittest.mock import patch, ANY

import pytest

from builder.packer import prepare_env, run_packer


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
        run_packer(tmp_path, "1234")

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
            run_packer(tmp_path, "1234")

    mock_popen.assert_called_once_with(
        ["make", "build-qemu-ubuntu-1234"],
        cwd=tmp_path,
        env=expected_env,
        stdout=ANY,
        stderr=ANY,
        universal_newlines=True,
    )

    proc.wait.assert_called_once_with()
