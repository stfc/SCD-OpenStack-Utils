#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation

echo "Content-Type: text/plain"
echo ""

instanceid=$QUERY_STRING

if [[ "$instanceid" =~ ^[0-9a-f-]+$ ]]; then
    source /etc/openstack-utils/username-openrc.sh
    userid=$(openstack server show "$instanceid" | grep user_id | cut -d'|' -f3)
    username=$(openstack user show "$userid" | grep name | cut -d '|' -f3)
    echo "$username"
fi
