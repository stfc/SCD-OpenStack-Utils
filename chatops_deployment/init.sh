#!/bin/bash

set -eux

if [ ! -f bastion-key ] || [ ! -f bastion-key.pub ]; then
  ssh-keygen -t rsa -b 4096 -f bastion-key -N "$PASSPHRASE"
fi

sudo snap install terraform
sudo apt update
sudo apt install python3-venv

if [ ! -d ansible_venv ]; then
  python3 -m venv ansible_venv
fi

ansible_venv/bin/python3 -m pip install ansible_venv
