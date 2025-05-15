# Variables

## Environments

The inventory and variables are separated by 2 environments folders. `dev` and `prod`. This allows us to change values
for specific deployments such as, updating the version of the Elastic stack used from `9.0.0 -> 10.0.0` on the **dev**
deployment before using the changes on production. We can also use a different ChatOps configuration targeting different
workspaces for testing and users.

The variables themselves should always remain identical in **dev** and **prod**. However, the values may change.

## Inventory

The inventory is made from both a dynamic **openstack.yml** and static **hosts.yml** file.

#### hosts.yml

Creates the parent groups **private** and **monitoring**.  
Hosts in the **private** group are machines in the private network that do not have a floating IP attached to them. 
This means we must use a jump host to connect to them and be able to execute Ansible code. The HAProxy host acts as the
jump host because despite it being in the private network itself, it has a floating IP attached to it.

The monitoring
