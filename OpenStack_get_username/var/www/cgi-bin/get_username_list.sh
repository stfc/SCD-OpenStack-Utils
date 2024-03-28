#!/bin/bash

echo "Content-Type: text/plain"
echo ""

instanceid=$QUERY_STRING
#instanceid=$1
#echo $instanceid

if [[ $instanceid =~ ^[0-9a-f\-]*$ ]];then
    source /etc/openstack-utils/username-openrc.sh

    userid="$(nice openstack server show -c user_id -f value "$instanceid")"
    projectid="$(nice openstack server show -c project_id -f value "$instanceid")"
    #echo $userid
    if (grouptag=$(openstack project show $projectid -f value -c tags | grep 'grouplogin=true')); then

    #username=`nice openstack user show $userid | grep name | cut -d '|' -f3`
        username="$(nice openstack role assignment list --project "$projectid" --names -c User -f value | cut -d'@' -f 1)"
    else
        username="$(nice openstack user show -c name -f value "$userid")"
    fi
    echo $username
#elif
#    echo "ERROR"
fi
