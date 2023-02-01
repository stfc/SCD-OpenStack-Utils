- Install secret from an existing krb5.keytab:

`kubectl create secret generic rabbit-consumer-keytab --from-file krb5.keytab`