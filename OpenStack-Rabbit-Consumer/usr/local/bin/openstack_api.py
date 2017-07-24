import logging
import requests
import common

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)


def authenticate(project_id):
    logger.info("Attempting to authenticate to Openstack")

    s = requests.Session()
    s.verify = "/etc/grid-security/certificates/"
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[503])
    s.mount('https://', HTTPAdapter(max_retries=retries))

    # https://developer.openstack.org/api-ref/identity/v3/#password-authentication-with-scoped-authorization
    data = { 
        "auth" : {
            "identity" : {
                "methods" : ["password"],
                "password" : {
                    "user" : {
                        "name" : common.config.get("openstack", "username"),
                        "domain" : { "name": common.config.get("openstack", "domain") },
                        "password" : common.config.get("openstack", "password")
                    }
                }
            },
            "scope" : {
                "project" : {
                    "id" : project_id
                }
            }
        }
    }
    response = s.post(common.config.get("openstack", "identity_url") + '/auth/tokens', json=data)

    if response.status_code != 201:
        logger.error("Authenticatication failure")
        raise Exception(str(response.status_code), response.text)

    logger.info("Authentication successful")

    return str(response.headers['X-Subject-Token'])


def update_metadata(project_id, instance_id, metadata):
    logger.info("Attempting to set new metadata for VM: %s - %s" % (instance_id, str(metadata)))

    s = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[503])
    s.mount('https://', HTTPAdapter(max_retries=retries))

    token = authenticate(project_id)

    headers = {'Content-type': 'application/json', "X-Auth-Token" : token}
    url = common.config.get("openstack", "compute_url") + '/%s/servers/%s/metadata' % (project_id, instance_id)

    response = s.post(url, headers=headers, json={"metadata" : metadata})

    if response.status_code != 200:
        logger.error("Setting metadata failed")
        raise Exception(str(response.status_code), response.text)

    logger.info("Setting metadata successful")
