# Deployment

## Contents:

- [Quick Start](#quick-start)

## Quick Start:

- If you are deploying from scratch, start at [Setting up localhost](#setting-up-localhost)
- If you already have the repository cloned, the vault password saved and the projects clouds.yaml then start
  at [Deploy infrastructure](#deploy-infrastructure).
- If you only need to make changes to an existing deployment then start
  at [Configure infrastructure](#configure-infrastructure)
- To destroy all infrastructure, see [Destroy infrastructure](#destroy-infrastructure)

## OpenStack Project Requirements:

The project `Cloud-MicroServices` is already setup with all the required requisites. The variables in this repository 
reference that project. If you are using a different project for a deployment not used by the Cloud Team you will 
require the following:

- A floating IP (e.g. 130.246.X.Y)
- DNS records:
  - `<your-domain> CNAME host-130-246-X-Y.nubes.stfc.ac.uk`
  - **AND**
  - ```
    # EITHER
    *.<your-domain> CNAME host-130-246-X-Y.nubes.stfc.ac.uk
    # OR
    kibana.<your-domain>.       CNAME   host-130-246-X-Y.nubes.stfc.ac.uk.
    grafana.<your-domain>.      CNAME   host-130-246-X-Y.nubes.stfc.ac.uk.
    prometheus.<your-domain>.   CNAME   host-130-246-X-Y.nubes.stfc.ac.uk.
    alertmanager.<your-domain>. CNAME   host-130-246-X-Y.nubes.stfc.ac.uk.
    chatops.<your-domain>.      CNAME   host-130-246-X-Y.nubes.stfc.ac.uk.
    ```
- Ports 80 and 443 open inbound from the internet
- OpenStack Volume for the VM ~10GB

### Deploying the Infrastructure:

You can run the deployment from any machine (including your local laptop).
However, we suggest you make a dedicated "seed VM" in OpenStack as the
deployment will create files such as SSL certificates and SSH keys which you
will need to keep for further maintenance.

Machine requirements:

- Python3
- Snap (to install Terraform)
- Pip or equivalent (to install Ansible)

#### Setting up localhost:

1. Install Ansible (preferably into a virtual environment) and collections
   ```shell
   # Using pip or another package manager
   pip install ansible
   
   # Install collections using Ansible Galaxy
   ansible-galaxy install -r requirements.yml  

   # Install dependencies
   pip install -r requirements.yml
   ```

2. Create a vault password file to avoid repeated inputs
   ```shell
   # Either
   
   echo "chatops_vault_password" >> ~/.chatops_vault_pass
   
   # or
   
   vim ~/.chatops_vault_pass # and enter the vault password as plain text
   ```

3. Change permissions and attributes to protect the file
   ```shell
   chmod 400 ~/.chatops_vault_pass
   chattr +i ~/.chatops_vault_pass
   ```
   
4. Copy the projects clouds.yaml to the `~/.config/openstack/clouds.yaml`
   ```shell
   cp <path-to>/clouds.yaml ~/.config/openstack/clouds.yaml
   ```

#### Deploy infrastructure:

You can deploy both development and production environments on the same machine but not at the same time.

1. Clone this repository
   ```shell
   git clone https://github.com/stfc/SCD-OpenStack-Utils
   ```

2. Change into the `ansible` directory
   ```shell
   cd SCD-OpenStack-Utils/chatops_deployment/ansible
   ```

3. Deploy infrastructure. Using -i to specify which inventory to use, dev or prod
   ```shell
   ansible-playbook deploy.yml --vault-password-file=~/.chatops_vault_pass -i <environment>
   ```

#### Configure infrastructure

1. Configure the VMs. This step will take ~15 minutes
   ```shell
   ansible-playbook configure.yml --vault-password-file=~./chatops_vault_pass -i <environment>
   ```

#### Destroy infrastructure

To destroy the infrastructure and all locally generated files run the destroy playbook.

1. Destroy the infrastructure and locally generated files
   ```shell
   ansible-playbook destroy.yml --vault-password-file=~./chatops_vault_pass -i <environment>
   ```

## Debugging:

### Terraform

To debug the Terraform deployment, it is best to use the Terraform directly rather than through Ansible.
When you run the deploy.yml playbook, a `terraform.tfvars` file is created which allows you to run the Terraform modules
separate to Ansible.

1. Ensure you have run deploy.yml at least once to generate the variables file `terraform.tfvars`

2. Change to the terraform directory
   ```shell
   # Assuming you are in the ansible directory
   cd ../terraform
   ```

3. Check and change Terraform workspace. Terraform separates environments into workspaces. Make sure you are using the
   correct workspace before making changes.
   ```shell
   # List all workspaces. You should see at most "default, dev, prod"
   terraform workspace list
   
   # Select the workspace you want to affect
   terraform workspace select <environment>
   ```

4. Now you can make changes to the deployment. It is advisable you only use the Terraform commands directly if there is
   something very wrong. The Ansible playbooks should be the first choice.
   ```shell
   # For example, plan and apply changes
   terraform plan -out plan
   terraform apply plan
   
   # Refresh the state to check API connections
   terraform refresh
   
   # Validate the config
   terraform validate
   ```
   
### Ansible

Each role in the Ansible playbook is tagged in its play. This enables you to run only parts of the playbooks. This is 
important as it takes ~15 minutes to run the entire playbook. So, when you only want to make changes to certain parts 
of the deployment you can use `--tags <some-tag>` to run only that part of the play.

For example, if you change the Prometheus config file template you can just run the playbook with the **prometheus** tag
.
```shell
ansible-playbook configure.yml --vault-password-file=~./chatops_vault_pass -i dev --tags prometheus
```

It is not recommended to use tags when making changes to the production deployment. As changes are promoted to 
production the entire playbook should be run. This avoids any changes being missed out and ensures the entire deployment
is running the latest configuration.
