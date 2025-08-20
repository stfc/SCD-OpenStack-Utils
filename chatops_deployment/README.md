# ChatOps Deployment

![Linting](https://github.com/stfc/SCD-OpenStack-Utils/actions/workflows/chatops.yaml/badge.svg)

## Contents

- [About](#about)

### About

This project outlines the deployment of the Cloud ChatOps application
found [here](https://github.com/stfc/cloud-docker-images/tree/master/cloud-chatops). The goal is to create an easily
deployable and highly available infrastructure to run the Docker container on. We achieve this by using Terraform and
Ansible to provision and configure a virtual machine the services will run on.

This includes:

- Load balanced application traffic
- Infrastructure-wide service logging to a central location
- Service monitoring with visual dashboards and alerting notifications
- Multi-environment deployment (e.g. dev, staging, prod)

To get started with the deployment, see [INSTALL.md](docs/INSTALL.md).

For information about what services are deployed, see [SERVICES.md](docs/SERVICES.md)

To understand what the Terraform modules do, see [TERRAFORM.md](docs/TERRAFORM.md)

To know what and where variables are stored, see [VARIABLES.md](docks/VARIABLES.md)
