# Terraform

## Contents:
- [What is created in OpenStack?](#what-is-created-in-openstack)
- [Terraform Modules](#terraform-modules)

## What is created in OpenStack?

All resources for this deployment can be automatically created and destroyed with the Ansible playbooks. 
The only exception to this is the floating IPs and Volumes.  

We don't automate the creation and deletion of FIPs because ports need to be opened and closed
by Digital Infrastructure (DI). DNS records are associated with specific FIPs which require a ticket to DI to change. 

We don't automate the creation and deletion of Volumes because they are used as a persistent data storage.
If we delete the volume we lose all the metrics and log data. There is currently no backup process in place.

See below a diagram of the OpenStack infrastructure:

![Terraform Infrastructure](chatops_terraform.svg)

## Terraform Modules

The Terraform configuration is made of 3 modules: the root module, compute and networking.

### [Root](../terraform)

#### [main.tf](../terraform/main.tf)

- OpenStack provider is declared, including what version to use and which clouds to get credentials from.
- Network module is loaded with input variables from `terraform.tfvars`.
- Compute module is loaded with input variables from `terraform.tfvars`.

#### [outputs.tf](../terraform/outputs.tf)

- Declares what variables to "export" into the Terraform state files.  
  This is where the VM IP addresses are gathered for the hosts file.
  We also extract the attached Volume paths for Prometheus and Elasticsearch

#### [variables.tf](../terraform/variables.tf)
 
- Declares what variables are required for the configuration to run correctly.

#### [terraform.tfvars](../terraform/terraform.tfvars)

> ***Note:*** This file won't exist unless the configuration has been deployed with Ansible

- Contains the variable values needed in `variables.tf`. These are generated from the Ansible variables

### [Compute](../terraform/modules/compute)

#### [main.tf](../terraform/modules/compute/main.tf)

> ***NOTE:*** The volumes and floating IP must already be present in the project. They are not created.

- OpenStack provider is declared, including what version to use and which clouds to get credentials from.
- SSH public key is imported into the OpenStack project.
- Service VMs are created: Grafana, Prometheus, Elastic, ChatOps, Load balancer.
- Volumes are attached to the Prometheus and Elastic VMs.
- Floating IP is associated to the Load balancer VM network port.

#### [outputs.tf](../terraform/modules/compute/outputs.tf)

- Exports the VM private IP addresses to Terraform state files.
- Exports the Volume attachment paths. E.g. `/dev/vdb`.

#### [variables.tf](../terraform/modules/compute/variables.tf)
 
- Makes all Terraform networking resources available to this module.

### [Networking](../terraform/modules/networking)

#### [main.tf](../terraform/modules/networking/main.tf)

- OpenStack provider is declared, including what version to use and which clouds to get credentials from.
- Private network, subnet and router are created
- Security groups for each service are created with specific rules for their requirements

#### [outputs.tf](../terraform/modules/networking/outputs.tf)

- Outputs the networking resources to be available in the compute module.

#### [variables.tf](../terraform/modules/networking/variables.tf)
 
- Makes the input variables available to this module.