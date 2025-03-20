#!/bin/bash

set -e

generate_hostname_data () {

	hostname_data=$(jq -n \
			--arg host "$host" \
			--arg current_time "$current_time" \
			--arg target_time "$target_time" \
			--arg name "$name" \
			--arg comment "$comment" \
			'{matchers: [
				{
					name: "hostname",
					value: $host,
					isRegex: false
				}
			],
			startsAt: $current_time,
			endsAt: $target_time,
			createdBy: $name,
			comment: $comment,
			status: {
					state: "active"
				}
			}')

}

generate_instance_data () {

	instance_data=$(jq -n \
                        --arg host "$host" \
                        --arg current_time "$current_time" \
                        --arg target_time "$target_time" \
                        --arg name "$name" \
                        --arg comment "$comment" \
                        '{matchers: [
                                {
                                        name: "instance",
                                        value: $host,
                                        isRegex: false
                                }
                        ],
                        startsAt: $current_time,
                        endsAt: $target_time,
                        createdBy: $name,
                        comment: $comment,
                        status: {
                                        state: "active"
                                }
                        }')
	
}

declare comment
declare current_time
declare host
declare host_list
declare name
declare password
declare silence_time
declare target_time

declare -a hosts

host_list=$1
silence_time=$2
name=$3
comment=$4

if [ -z "$silence_time" ]
then
	silence_time="1"
else
	silence_time=$(echo "$silence_time" | cut -d "d" -f1)
fi

read -r -s -p "Alertmanager admin password: " password

current_time=$(date +"%Y-%m-%dT%T.%NZ")

target_time=$(date +"%Y-%m-%dT10:00:00.000Z" -d "+$silence_time days")

mapfile -d , -t hosts < <( printf '%s' "$host_list" )

for host in "${hosts[@]}"
do
	generate_hostname_data
	generate_instance_data
	curl --user admin:"$password" https://openstack.stfc.ac.uk:9093/api/v2/silences -H "Content-Type: application/json" -d "$hostname_data"
	curl --user admin:"$password" https://openstack.stfc.ac.uk:9093/api/v2/silences -H "Content-Type: application/json" -d "$instance_data"
done
