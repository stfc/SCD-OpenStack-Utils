import logging
from dataclasses import dataclass
from typing import Dict, Optional

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig

logger = logging.getLogger(__name__)


@dataclass
class VaultMetadata(DataClassDictMixin):
    """
    Deserialised metadata that is set a VM's metadata
    """

    vault_group: str
    vault_role: str

    # pylint: disable=too-few-public-methods
    class Config(BaseConfig):
        """
        Sets the aliases for the metadata keys
        """

        aliases = {
            "vault_group": "VAULT_GROUP",
            "vault_role": "VAULT_ROLE",
        }

    def override_from_vm_meta(self, vm_meta: Dict[str, str]):
        """
        Overrides the values in the metadata with the values from the VM's
        metadata
        """
        for attr, alias in self.Config.aliases.items():
            if alias in vm_meta:
                setattr(self, attr, vm_meta[alias])
