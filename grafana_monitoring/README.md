# Ansible Deployment of Cloud Grafana

## What?
An Ansible playbook to deploy our staging / production Grafana instances. It installs Grafana with HAProxy and uses a bash script to clone our [dashboard repository](https://github.com/stfc/cloud-grafana-dashboards) to the Grafana provisioning folder. The bash script is also run with cron to keep the dashboards up-to-date..

## Why?
To replace the Aquilon configuration...

## How?

#### Note: You will need to have a floating IP with DNS and ports 80, 443 open. You must set up a load balancer and add the VM as a member to both pools beforehand.

1. Clone this repository
    ```shell
    git clone https://github.com/stfc/SCD-OpenStack-Utils
    ```
2. Install ansible with pip (with a virtual environment)
    ```shell
    sudo apt install python3-venv
    python3 -m venv ansible
    source ansible/bin/activate
    pip install ansible
    ```
3. By default, the hosts file includes both the dev and prod grafana instance domains.
If you want to run the playbook on only one of these instances you need to uncomment the corresponding host in the inventory.
   ```ini
   # Contents of: ./hosts.ini
   [grafana]
   # grafana.nubes.rl.ac.uk
   # dev-grafana.nubes.rl.ac.uk
   ```
3. Run the ansible playbook
    ```shell
    ansible-playbook site.yaml --inventory hosts
    ```
4. If you need to make changes to any of the services' config you can run each role separately with their tags
    ```shell
    ansible-playbook site.yaml --inventory hosts --tags <grafana | haproxy | certbot>
    ```
   