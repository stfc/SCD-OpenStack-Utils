import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from rabbit_consumer.common import RabbitConsumer

logger = logging.getLogger(__name__)


def authenticate(project_id):
    logger.info("Attempting to authenticate to Openstack")

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[503])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    # https://developer.openstack.org/api-ref/identity/v3/#password-authentication-with-scoped-authorization
    data = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": RabbitConsumer.get_env_str("OPENSTACK_USERNAME"),
                        "domain": {
                            "name": RabbitConsumer.get_env_str("OPENSTACK_DOMAIN_NAME")
                        },
                        "password": RabbitConsumer.get_env_str("OPENSTACK_PASSWORD"),
                    }
                },
            },
            "scope": {"project": {"id": project_id}},
        }
    }
    response = session.post(
        RabbitConsumer.get_env_str("OPENSTACK_AUTH_URL") + "/auth/tokens",
        json=data,
    )

    if response.status_code != 201:
        logger.error("Authentication failure")
        raise ConnectionRefusedError(f"{response.status_code}: {response.text}")

    logger.debug("Authentication successful")

    return str(response.headers["X-Subject-Token"])


def update_metadata(project_id, instance_id, metadata):
    logger.info(
        "Attempting to set new metadata for VM: %s - %s", instance_id, str(metadata)
    )

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[503])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    token = authenticate(project_id)

    headers = {"Content-type": "application/json", "X-Auth-Token": token}
    url = (
        RabbitConsumer.get_env_str("OPENSTACK_COMPUTE_URL")
        + f"/{project_id}/servers/{instance_id}/metadata"
    )

    response = session.post(url, headers=headers, json={"metadata": metadata})

    if response.status_code != 200:
        logger.error("Setting metadata failed")
        raise ConnectionAbortedError(f"{response.status_code}: {response.text}")

    logger.debug("Setting metadata successful")
