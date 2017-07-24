import logging
import requests
import common
import subprocess

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests_kerberos import HTTPKerberosAuth


MAKE_SUFFIX = "/host/{0}/command/make"
MANAGE_SUFFIX = "/host/{0}/command/manage?hostname={0}&{1}={2}&force=true"

logger = logging.getLogger(__name__)


def verify_kerberos_ticket():
    logger.info("Checking for valid Kerberos Ticket")

    if subprocess.call(['klist', '-s']) == 1:
        logger.warn("No ticket found / expired. Obtaining new one")
        kinit_cmd = ['kinit', '-k']

        if common.config.get("kerberos", "suffix") != "":
            kinit_cmd.append(common.config.get("kerberos", "suffix"))

        subprocess.call(kinit_cmd)

        if subprocess.call(['klist', '-s']) == 1:
            raise Exception("Failed to obtain valid Kerberos ticket")

    logger.info("Kerberos ticket success")
    return True


def aq_make(hostname, personality=None, osversion=None, archetype=None, osname=None):
    logger.info("Attempting to make templates for " + hostname)

    # strip out blank parameters and hostname
    params = {k: v for k, v in locals().items() if v is not None and k != "hostname"}

    # join remaining parameters to form url string
    params = [k + "=" + v for k, v in params.items()]

    url = common.config.get("aquilon", "url") + MAKE_SUFFIX.format(hostname) + "?" + "&".join(params)

    verify_kerberos_ticket()

    s = requests.Session()
    s.verify = "/etc/grid-security/certificates/"
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[503])
    s.mount('https://', HTTPAdapter(max_retries=retries))

    response = s.post(url, auth=HTTPKerberosAuth())

    if response.status_code != 200:
        logger.error("Aquilon make failed: " + str(response.text))
        logger.error(url)
        raise Exception("Aquilon make failed")

    logger.info("Successfully made templates")


def aq_manage(hostname, env_type, env_name):
    logger.info("Attempting to manage %s to %s %s" % (hostname, env_type, env_name))

    url = common.config.get("aquilon", "url") + MANAGE_SUFFIX.format(hostname, env_type, env_name)

    verify_kerberos_ticket()

    s = requests.Session()
    s.verify = "/etc/grid-security/certificates/"
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[503])
    s.mount('https://', HTTPAdapter(max_retries=retries))

    response = s.post(url, auth=HTTPKerberosAuth())

    if response.status_code != 200:
        logger.error("Aquilon manage failed: " + str(response.text))
        logger.error(url)
        raise Exception("Aquilon manage failed")

    logger.info("Successfully managed machine")


def vm_create(hostname, domain=None, sandbox=None, personality=None, osversion=None, archetype=None, osname=None):
    if domain:
        aq_manage(hostname, "domain", domain)
    else:
        aq_manage(hostname, "sandbox", sandbox)

    aq_make(hostname, personality, osversion, archetype, osname)


def vm_delete(hostname):
    # manage the host back to prod
    aq_manage(hostname, "domain", "prod")

    # reset personality etc ...
    aq_make(hostname, "nubesvms", "6x-x86_64", "ral-tier1", "sl")

