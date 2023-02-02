- Install secret from an existing krb5.keytab:

`kubectl create secret generic rabbit-consumer-keytab --from-file krb5.keytab`

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

- TODO Overlay descriptions