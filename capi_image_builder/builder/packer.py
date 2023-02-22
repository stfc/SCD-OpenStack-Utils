import os
import shutil
import subprocess
from pathlib import Path

from builder.args import Args

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


def run_packer_build(packer_dir: Path, ubuntu_version: str):
    """Run packer to build a target."""
    print(f"Running packer build in {packer_dir}...")
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


def get_image_path(packer_dir: Path) -> Path:
    """
    Returns the path to the image file that was built from
    the CAPI packer directory
    """
    output_dir = packer_dir / "output"
    output_files = [file for file in output_dir.rglob("*") if file.is_file()]

    # Do some basic checks
    if len(output_files) != 1:
        raise RuntimeError("Expected exactly one file in the output directory.")

    output_file = output_files[0]
    gigabyte = 1024 * 1024 * 1024  # bytes
    if os.path.getsize(output_file) < gigabyte:
        raise RuntimeError(
            "Output file is less than 1GB. This is probably not an image."
        )

    return output_file


def clear_output_directory(packer_dir: Path):
    """
    Clears the output directory of any existing files.
    """
    output_dir = packer_dir / "output"
    if output_dir.exists():
        shutil.rmtree(output_dir)


def build_image(args: Args) -> Path:
    """
    Builds an updated image and returns the path to the
    resulting image file path
    """
    packer_dir = get_packer_dir_from_repo_root(Path(args.target_dir))
    clear_output_directory(packer_dir)
    run_packer_build(packer_dir, args.os_version)
    return get_image_path(packer_dir)
