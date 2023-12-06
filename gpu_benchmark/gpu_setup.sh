#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation

sudo dnf update -y

# # Nvidia drivers - centos8
echo 'blacklist nouveau
options nouveau modeset=0' > /usr/lib/modprobe.d/blacklist-nouveau.conf
echo "Updating dracut"
sudo dracut --force
(lsmod | grep -wq nouveau && echo "Rebooting to disable nouveau" && sudo reboot) || true

sudo dnf install tar bzip2 make automake gcc gcc-c++ pciutils elfutils-libelf-devel libglvnd-devel -y
sudo dnf install -y kernel-devel kernel-headers -y
wget -nc https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
nvidia-smi || sudo sh cuda_12.1.0_530.30.02_linux.run --silent
nvidia-smi || (echo "Rebooting machine to load Nvidia Driver" && sudo reboot)