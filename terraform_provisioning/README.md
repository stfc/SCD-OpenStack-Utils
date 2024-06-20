# terraform_privisioning
* This folder contains terraform scripts to manage openstack configurations
* These require a `clouds.yaml` in `~/.config/openstack/` to provide authentication

## priv_network.tf
* This terraform scripts creates a private network with a subnet domain of `10.0.0.x`
* It also adds a router to connect the private network to the external network
* You must provide a external_network_id to connect to router to
* The script must be run with `--var-file=vars.tfvars` to pass through the required variables
