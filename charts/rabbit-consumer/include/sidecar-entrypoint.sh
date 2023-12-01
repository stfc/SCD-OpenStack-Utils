#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation

set -ex

dnf install -y krb5-workstation

echo "Principle set to: $KRB5_PRINCIPLE"

useradd -r krb5user
# Run kinit.sh as system user to reduce risk of privilege escalation
su --preserve-environment -c '/etc/entrypoints.d/kinit.sh' krb5user

# We should never get here
echo "ERROR: Exited while loop"
exit 1
