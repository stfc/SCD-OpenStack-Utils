#!/bin/bash

set -eux

if [ ! -f ~/.config/openstack/clouds.yaml ]; then
  printf "Could not find %s/.config/openstack/clouds.yaml.\nPlease make sure you have a valid clouds.yaml in this location.\n" "$HOME"
  exit
fi

PLAN="plan-$(date +%F)"
PROJECT_ROOT=$(pwd)

cd terraform
terraform init
terraform refresh
terraform plan -out "$PLAN"
terraform apply "$PLAN" -auto-approve
terraform output > tf_outputs.txt

cd "$PROJECT_ROOT"

sed -r '
  s/_host_ips = \[//;
  s/[",]//g;
  s/ //g;
  s/]//g;
  s/([a-z]+)[^\n]*/[\1]/;
' terraform/tf_outputs.txt > ansible/hosts.ini