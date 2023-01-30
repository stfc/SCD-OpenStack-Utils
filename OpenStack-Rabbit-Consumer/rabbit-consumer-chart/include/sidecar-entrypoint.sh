#!/bin/bash

set -ex

dnf install -y krb5-workstation
echo "installed"
cat /etc/krb5.conf
sleep infinity
