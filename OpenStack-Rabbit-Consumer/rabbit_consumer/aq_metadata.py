import logging
from dataclasses import dataclass
from typing import Dict

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig

logger = logging.getLogger(__name__)


@dataclass
class AqMetadata(DataClassDictMixin):
    """
    Deserialised metadata that is set either on an Openstack image
    or a VM's metadata
    """

    aq_archetype: str
    # Aq domain can hold either a domain or sandbox reference
    aq_domain: str

    aq_personality: str
    aq_os_version: str
    aq_os: str

    class Config(BaseConfig):
        aliases = {
            "aq_archetype": "AQ_ARCHETYPE",
            "aq_domain": "AQ_DOMAIN",
            "aq_personality": "AQ_PERSONALITY",
            "aq_os_version": "AQ_OSVERSION",
            "aq_os": "AQ_OS",
        }

    def override_from_vm_meta(self, vm_meta: Dict[str, str]):
        """
        Overrides the values in the metadata with the values from the VM's
        metadata
        """
        for attr, alias in self.Config.aliases.items():
            if alias in vm_meta:
                setattr(self, attr, vm_meta[alias])

        if "AQ_SANDBOX" in vm_meta:
            self.aq_domain = vm_meta["AQ_SANDBOX"]
