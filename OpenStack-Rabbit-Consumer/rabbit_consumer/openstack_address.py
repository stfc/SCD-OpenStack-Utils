import logging
import socket
from dataclasses import dataclass, field
from typing import Dict, Optional

from mashumaro import DataClassDictMixin, field_options

logger = logging.getLogger(__name__)


@dataclass
class OpenstackAddress(DataClassDictMixin):
    """
    Deserializes the Openstack API response for a server's
    network addresses. This is expected to be called from the
    OpenstackAPI. To get an actual list use the Openstack API.
    """

    version: int
    addr: str
    mac_addr: str = field(metadata=field_options(alias="OS-EXT-IPS-MAC:mac_addr"))
    hostname: Optional[str] = None

    @staticmethod
    def get_internal_networks(addresses: Dict) -> list["OpenstackAddress"]:
        """
        Returns a list of internal network addresses. This
        is expected to be called from the OpenstackAPI. To get an actual
        list use the Openstack API wrapper directly.
        """
        internal_networks = []
        for address in addresses["Internal"]:
            found = OpenstackAddress.from_dict(address)
            found.hostname = OpenstackAddress.convert_hostnames(found.addr)
            internal_networks.append(found)
        return internal_networks

    @staticmethod
    def convert_hostnames(ip_addr: str) -> str:
        try:
            return socket.gethostbyaddr(ip_addr)[0]
        except socket.herror:
            logger.info("No hostname found for ip %s", ip_addr)
            raise
        except Exception:
            logger.error("Problem converting ip to hostname")
            raise
