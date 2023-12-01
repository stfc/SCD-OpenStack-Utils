#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
import sys
import os
import json
from subprocess import check_output, Popen, PIPE
from shlex import quote
import cgi

project_id = sys.argv[1]

env = os.environ.copy()

sourcecmd = "source /etc/openstack-utils/username-openrc.sh;"


def cl(c):
    p = Popen(sourcecmd+c, shell=True, stdout=PIPE, env=env)
    return p.communicate()[0]

print("Content-Type: application/json")
print("")

arguments = cgi.FieldStorage()
for i in arguments.keys():
    print(i + ": " + arguments[i].value)

assignment_out = cl("openstack role assignment list --project " + quote(project_id) + " -f json")
assignments = json.loads(assignment_out)
mapping_out = cl("openstack mapping show irisiam -f json")
mapping_json = json.loads(mapping_out)

rules = mapping_json['rules']
groups_in_project = []
iam_allowed_groups = {
    "groups": []
}

for assignment in assignments:
    if assignment['Group'] != "":
        groups_in_project.append(assignment['Group'])

for rule in rules:
    locals = rule['local']
    remotes = rule['remote']

    for local in locals:
        if local['group']['id'] in groups_in_project:
            for remote in remotes:
                if remote['type'] == "OIDC-groups":
                    iam_allowed_groups['groups'].extend(remote['any_one_of'])

print(json.dumps(iam_allowed_groups))
