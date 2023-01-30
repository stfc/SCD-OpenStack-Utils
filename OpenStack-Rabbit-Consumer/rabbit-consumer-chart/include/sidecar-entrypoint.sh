#!/bin/bash

set -ex

dnf install -y krb5-workstation

cat /etc/krb5.conf
mkdir /shared/krb5cc

sleep infinity
