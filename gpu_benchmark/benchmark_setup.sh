#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 United Kingdom Research and Innovation
set -ex

OS_NAME=$(awk -F= '/^NAME=/{gsub("\"","",$2); print $2}' /etc/os-release)

case "$OS_NAME" in
  "Ubuntu"*)
    git clone https://github.com/phoronix-test-suite/phoronix-test-suite.git
    cd phoronix-test-suite/
    sudo ./install-sh
    sudo apt install xvfb -y
    sudo apt-get install php-cli php-xml -y
    sudo reboot now
    ;;
  "Rocky Linux"*)
    sudo dnf install phoronix-test-suite xorg-x11-server-Xvfb -y
    ;;
esac

