# Variables

## Environments

The inventory and variables are separated by 2 environments folders. `dev` and `prod`. This allows us to change values
for specific deployments such as, changing the version of the ChatOps application used from `9.0.0 -> 10.0.0` on the **dev**
deployment before using the changes on production. We can also use a different ChatOps configuration targeting different
workspaces for testing and users.

The variable keys should always remain identical in **dev** and **prod**. However, the values may change.

## Inventory

The inventory is made from the static **hosts.yml**. The contents of this file should not be changed unless you are
using a different DNS record.

#### hosts.yml

Creates a single group called **stack** with one host which is the stack VM. It also sets the local SSH key to use for 
running Ansible commands.
