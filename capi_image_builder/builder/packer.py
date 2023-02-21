import os
import shutil
import subprocess
from pathlib import Path

# Relative dir of STFC vars from capi dir
PACKER_VARS_FILE = "packer/config/stfc.json"


def get_packer_dir_from_repo_root(repo_root: Path) -> Path:
    """Get the path to the packer dir from the repo root."""
    return repo_root / "images" / "capi"


def prepare_env(packer_dir: Path) -> dict:
    """
    Prepares an environment for packer to pick up
    the STFC vars file with our customisations.
    """
    current_env = os.environ.copy()
    current_env["PACKER_VAR_FILES"] = (packer_dir / PACKER_VARS_FILE).as_posix()
    return current_env


def run_packer(packer_dir: Path, ubuntu_version: str):
    """Run packer to build a target."""
    with subprocess.Popen(
        ["make", f"build-qemu-ubuntu-{ubuntu_version}"],
        cwd=packer_dir,
        env=prepare_env(packer_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    ) as proc:
        for line in proc.stdout:
            print(line, end="")

        for line in proc.stderr:
            print(line, end="")
        proc.wait()

        if proc.returncode != 0:
            raise RuntimeError("Packer build failed")


def clear_output_directory(packer_dir: Path):
    output_dir = packer_dir / "output"
    if output_dir.exists():
        shutil.rmtree(output_dir)
