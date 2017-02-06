#!/bin/bash

echo "Content-Type: text/plain"
echo ""

instanceid=$QUERY_STRING
#instanceid=$1
if [[ $instanceid =~ ^[0-9a-f\-]*$ ]];then
    source /etc/openstack-utils/username-openrc.sh

    userid=`openstack server show $instanceid | grep user_id | cut -d'|' -f3`
    #echo $userid

    username=`openstack user show $userid | grep name | cut -d '|' -f3`
    echo $username
fi
