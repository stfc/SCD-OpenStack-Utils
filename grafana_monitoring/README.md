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
3. Make an IRIS IAM client with the redirect URI of:
    ```
    https://<your-domain>:443/login/generic_oauth
    ```
4. Fill in the staging or production inventory with the credentials
5. Change the `grafana` group inventory hosts to whatever IP the machine will be running on.
6. Run the ansible playbook
    ```shell
    ansible-playbook site.yaml --inventory <staging | production>
    ```
7. If you need to make changes to any of the services' config you can run each role separately with their tags
    ```shell
    ansible-playbook site.yaml --inventory <staging | production> --tags <grafana | haproxy | certbot>
    ```
   