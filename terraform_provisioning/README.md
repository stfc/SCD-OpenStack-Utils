# terraform_privisioning
* This folder contains terraform scripts to manage openstack configurations
* These require a `clouds.yaml` in `~/.config/openstack/` to provide authentication

## Running the scripts
* The scripts require the terraform package to be installed
    * To install terraform on ubuntu or any ubuntu derivative with snap installed:
```bash
snap install terraform --classic
```
* If you are confused please find further info [here](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
* To actually run the script, start by entering the directory of the script you want to run, e.g.:
```bash
cd load_balancing_application
```
* Then generate a plan, this will also tell you what actions terraform will perform:
    * Note this will generate a plan file in the current directory
```bash
terraform plan -out plan --var-file=vars.tfvars
```
* After that, to actually "apply" the changes planned in the plan:
```bash
terraform apply plan
```
* To revert the changes, e.g. to change the number of instances, use:
```bash
terraform destroy --var-file=vars.tfvars
```

## private_network
* This terraform script creates a private network with a subnet domain of `10.0.0.x`
* It also adds a router to connect the private network to the external network
* You must provide a external_network_id to connect to router to
* The script must be run with `--var-file=vars.tfvars` to pass through the required variables

## load_balancing_application 
* This terraform script creates a private network and sets up two pools along with a load balancer
* In one of the pools ssh traffic will be directed to a bastion vm to access the application vm's
* The other pool contains the application vm's which the load balancer can pick from
* A private key is created in the script and then passed into the bastion vm to provide access to the application vm's
* You must provide: 
	* A external_network_id to connect to router to
	* A floating IP for the load balancer in order to connect to the vm's and bastion 
	* A image name for the bastion and web vm's
	* A flavour name for the bastion and web vm's also
	* A key pair to place on the bastion vm in order for you to access it
	* The number of instances of the web vm to be created in order for effective load balancing 
* Note you must use the ssh jumphost to access an application vm
