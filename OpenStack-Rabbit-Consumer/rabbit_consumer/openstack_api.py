import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from rabbit_consumer.rabbit_consumer import RabbitConsumer
from rabbit_consumer.consumer_config import ConsumerConfig

logger = logging.getLogger(__name__)


def authenticate(project_id):
    logger.info("Attempting to authenticate to Openstack")

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[503])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    config = ConsumerConfig()

    # https://developer.openstack.org/api-ref/identity/v3/#password-authentication-with-scoped-authorization
    data = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": config.openstack_username,
                        "domain": {"name": config.openstack_domain_name},
                        "password": config.openstack_password,
                    }
                },
            },
            "scope": {"project": {"id": project_id}},
        }
    }
    response = session.post(
        f"{config.openstack_auth_url}/auth/tokens",
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
        f"{ConsumerConfig().openstack_compute_url}"
        "/{project_id}/servers/{instance_id}/metadata"
    )

    logger.debug("POST: %s", url)
    response = session.post(url, headers=headers, json={"metadata": metadata})

    if response.status_code != 200:
        logger.error("Setting metadata failed")
        logger.error("POST URL: %s", url)
        raise ConnectionAbortedError(f"{response.status_code}: {response.text}")

    logger.debug("Setting metadata successful")
