#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 United Kingdom Research and Innovation
set -ex

DRIVER_VER="590"
OS_NAME=$(awk -F= '/^NAME=/{gsub("\"","",$2); print $2}' /etc/os-release)

case "$OS_NAME" in
  "Ubuntu"*)
    sudo apt update -y
    sudo apt install nvidia-driver-"$DRIVER_VER" -y
   ;;

"Rocky Linux"*)
    sudo dnf update -y

    echo 'blacklist nouveau
    options nouveau modeset=0' > /usr/lib/modprobe.d/blacklist-nouveau.conf
    echo "Updating dracut"
    sudo dracut --force
    (lsmod | grep -wq nouveau && echo "Rebooting to disable nouveau" && sudo reboot) || true

    sudo dnf install tar bzip2 make automake gcc gcc-c++ pciutils elfutils-libelf-devel libglvnd-devel -y
    sudo dnf install -y kernel-devel kernel-headers -y

    VERSION=$(awk -F= '/^VERSION_ID=/ {gsub("\"","",$2); print $2}' /etc/os-release 2>/dev/null || true)

    sudo dnf config-manager --add-repo http://developer.download.nvidia.com/compute/cuda/repos/rhel"${VERSION%%.*}"/"$(uname -m)"/cuda-rhel"${VERSION%%.*}".repo
    sudo dnf install nvidia-driver-assistant -y 
    nvidia-smi || nvidia-driver-assistant --install --branch "$DRIVER_VER" --module-flavor closed
    ;;
  *)
    echo "Please run on a Rocky or Ubuntu system" >&2
    exit 1
    ;;
esac
(echo "Rebooting machine to load Nvidia Driver" && sudo reboot)
