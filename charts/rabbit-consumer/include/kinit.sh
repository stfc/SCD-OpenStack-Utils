#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation

# Adapted from https://cloud.redhat.com/blog/kerberos-sidecar-container

set -ex

while true

do
echo "kinit at $(date --universal)"

kinit -V -k $KRB5_PRINCIPLE
# Check that the ticket is valid and echo the ticket
klist -c /shared/krb5cc -s && klist -c /shared/krb5cc

echo "$(date --universal): Waiting for $PERIOD_SECONDS seconds..."
sleep $PERIOD_SECONDS

done