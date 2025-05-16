# ChatOps Deployment
![Linting](https://github.com/stfc/SCD-OpenStack-Utils/actions/workflows/chatops.yaml/badge.svg)

## Contents:
- [About](#about)
- [Services](#services)

### About:
This project outlines the deployment of the Cloud ChatOps application found 
[here](https://github.com/stfc/cloud-docker-images/tree/master/cloud-chatops).<br>
The goal is to create an easily deployable and highly available infrastructure to run the image on.<br>

This includes:
- Load balanced application traffic
- Infrastructure wide service logging to a central location
- Service monitoring with visual dashboards and alerting notifications
- Multi-environment deployment (e.g. dev, staging, prod)

### Services
![ChatOps Services](docs/chatops_services.svg "Diagram of ChatOps Services")
