#!/bin/bash

set -ex

apt-get update \
&& DEBIAN_FRONTEND=noninteractive apt-get install -y krb5-user

while true; do ls /shared; sleep 10; done
