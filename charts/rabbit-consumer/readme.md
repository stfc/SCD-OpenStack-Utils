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
helm repo add scd-utils https://stfc.github.io/SCD-OpenStack-Utils
helm upgrade --install rabbit-consumer scd-utils/rabbit-consumer-chart -f values.yaml -f <template.yaml>
```

Upgrades
========

Upgrades are similarly handled:
```
helm upgrade rabbit-consumer scd-utils/rabbit-consumer-chart  -f values.yaml -f <template.yaml>
```

If required a version can be specified:
```
helm upgrade rabbit-consumer scd-utils/rabbit-consumer-chart  -f values.yaml -f <template.yaml> --version <version>
```

Startup
=======

The pod may fail 1-3 times whilst the sidecar spins up, authenticates and caches the krb5 credentials. During this time the consumer will start, check for the credentials and terminate if they are not ready yet.

The logs can be found by doing
`kubectl logs deploy/rabbit-consumers -n rabbit-consumer -c <container>`

Where `<container>` is either `kerberos` or `consumer` for the sidecar / main consumers respectively. 

Updating This Chart
=========================
If you have made changes to the Openstack-Rabbit-Consumer directory, you will need to update the version of the docker image used in this chart.
If you have updated the chart itself, you will need to update the version of the chart. But you can skip updating the image if appropriate.

(Sister dir)
- Open a PR to bump the version of the docker image in the Openstack-Rabbit-Consumer directory.
- Once merged, the new image will be pushed to the repository.

(This dir)
- Once a new image is available, the version in the helm chart needs to be updated. This is done by editing the `Chart.yaml` file and updating the `appVersion` field.
- Update the chart version to reflect the changes. Minor changes (such as the image version) should increment the patch version. Changes to this chart should increment the major/minor/patch according to SemVer guidance.
