FROM python:3.10

WORKDIR /usr/src/app

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
    krb5-user \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV AQ_ARCHETYPE=NOT_SET \
    AQ_DOMAIN=NOT_SET \
    AQ_PERSONALITY=NOT_SET \
    AQ_PREFIX=NOT_SET \
    AQ_URL=NOT_SET \
    AQ_FQDN=NOT_SET

ENV RABBIT_HOST=NOT_SET \
    RABBIT_PORT=NOT_SET \
    RABBIT_USERNAME=NOT_SET \
    RABBIT_PASSWORD=NOT_SET

ENV OPENSTACK_AUTH_URL=NOT_SET \
    OPENSTACK_CA_CERT=NOT_SET \
    OPENSTACK_COMPUTE_URL=NOT_SET \
    OPENSTACK_DOMAIN_NAME=NOT_SET \
    OPENSTACK_PROJECT_ID=NOT_SET \
    OPENSTACK_USERNAME=NOT_SET \
    OPENSTACK_PASSWORD=NOT_SET

ENV LOG_LEVEL=INFO

CMD [ "python", "./entrypoint.py"]
