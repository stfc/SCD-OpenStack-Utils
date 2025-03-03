# Ansible Deployment of Cloud Grafana

## What?
An Ansible playbook to deploy our staging / production Grafana instances. It installs Grafana with HAProxy and uses a bash script to clone our [dashboard repository](https://github.com/stfc/cloud-grafana-dashboards) to the Grafana provisioning folder. The bash script is also run with cron to keep the dashboards up-to-date..

## Why?
To replace the Aquilon configuration...

## How?
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
5. (Optional): Change the `grafana` group inventory hosts to whatever IP they are running on
6. Copy your SSL certificate with name format `<your-domain>.crt` to `roles/haproxy/files/` and make sure the key is prepended to the top.
7. Run the ansible playbook
    ```shell
    anisble-playbook run site.yaml --inventory staging/production
    ```
8. If you need to make changes to either the Grafana or HAProxy config you can run each role separately with their tags
    ```shell
    anisble-playbook run site.yaml --inventory staging/production --tags grafana
    # or
    anisble-playbook run site.yaml --inventory staging/production --tags haproxy
    ```
   