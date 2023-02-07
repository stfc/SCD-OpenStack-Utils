Cluster Prep
============

This application does not require persistent storage and is completely standalone.

- Install secret from an existing krb5.keytab, this should match the principle used in the values.yaml file:

`kubectl create secret generic rabbit-consumer-keytab --from-file krb5.keytab -n rabbit-consumer`

- Install secrets for the Rabbit and Openstack credentials
  based on the following .yaml template:

```
kind: Namespace
apiVersion: v1
metadata:
  name: rabbit-consumer
  labels:
    name: rabbit-consumer
---
apiVersion: v1
kind: Secret
metadata:
  # This should match the values.yaml values
  name: openstack-credentials
  namespace: rabbit-consumer  
type: Opaque
stringData:
  OPENSTACK_USERNAME:
  OPENSTACK_PASSWORD:
---
apiVersion: v1
kind: Secret
metadata:
  name: rabbit-credentials
  namespace: rabbit-consumer
type: Opaque
stringData:
  RABBIT_USERNAME:
  RABBIT_PASSWORD:
```

Environment Templates
=====================

Multiple values files are provided to target various environments:

- values.yaml: Attributes common to all environments (e.g. Aquilon URL)
- dev-values.yaml: Attributes for the dev Openstack environment. This assumes the PR is merged as it points to the `qa` tag.
- prod-values.yaml: Attributes for production. This does not include the tag, instead relying on the app version in Chart.yaml
- staging-values.yaml: Targets the dev Openstack environment, but pulls the latest build from the most recent PR. (Typically used to test before merging)

First Deployment
=================

The correct template needs to be selected from above, where `<template.yaml>` is the placeholder:

```
cd rabbit-consumer-chart && \
helm install rabbit-consumers . -f values.yaml -f <template.yaml>
```

Upgrades
========

Upgrades are similarly handled:
```
cd rabbit-consumer-chart && \
helm upgrade rabbit-consumers . -f values.yaml -f <template.yaml>
```

Startup
=======

The pod may fail 1-3 times whilst the sidecar spins up, authenticates and caches the krb5 credentials. During this time the consumer will start, check for the credentials and terminate if they are not ready yet.

The logs can be found by doing
`kubectl logs deploy/rabbit-consumers -n rabbit-consumer -c <container>`

Where `<container>` is either `kerberos` or `consumer` for the sidecar / main consumers respectively. 

Updating Prod
=============

Currently the CI only builds images targeting dev. This is because we should tag our prod images with semver (e.g. v1.0.0).

As we are currently using a mixed repository we can't rely on release tags in Github. For simplicity it's the developers responsibility to:

- Appropriately update the semver in `Charts.yaml`
- Build, tag and upload to Harbor, where tag is the semver:

```
docker build . -t harbor.stfc.ac.uk/stfc-cloud/openstack-rabbit-consumer:<tag>
docker push harbor.stfc.ac.uk/stfc-cloud/openstack-rabbit-consumer:<tag>
```
- Pull to the new chart version for prod
- Monitor (and potentially rollback) the new version using Helm
