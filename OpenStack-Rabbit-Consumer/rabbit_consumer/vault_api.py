import logging
from typing import List

import hvac

from rabbit_consumer.consumer_config import ConsumerConfig

logger = logging.getLogger(__name__)


class VaultClient:
    """
    Wrapper for Vault client.
    """

    def __init__(self):
        self.client = None

    def __enter__(self):
        self.client = hvac.Client(url=ConsumerConfig().vault_url, verify=False)
        self.client.auth.approle.login(
            role_id=ConsumerConfig().vault_role_id,
            secret_id=ConsumerConfig().vault_secret_id,
            mount_point="admin",
        )
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.logout()


def is_authenticated():
    """
    Checks for successful authenticaion with Vault
    """
    with VaultClient() as client:
        assert client.is_authenticated()


def check_vault_group_exists(vault_group: str) -> bool:
    """
    Checks given group mount point exists in vault
    """
    with VaultClient() as client:
        try:
            client.sys.read_auth_method_tuning(path=vault_group)
            return True
        except:
            logger.warning("Vault group %s not found", vault_group)
            return False


def check_approle_exists(approle: str, vault_group: str) -> bool:
    """
    Checks if AppRole exists in Vault group
    """
    logger.info("Checking AppRole %s exists", approle)
    with VaultClient() as client:
        try:
            client.auth.approle.read_role(role_name=approle, mount_point=vault_group)
            return True
        except:
            logger.warning(
                "Vault approle %s not found in group %s", approle, vault_group
            )
            return False


def get_wrapped_secret_id(approle, vault_group, vm_uuid) -> str:
    """
    Requests wrapped secret id from Vault for an Approle
    """
    with VaultClient() as client:
        return client.auth.approle.generate_secret_id(
            role_name=approle,
            mount_point=vault_group,
            wrap_ttl="600s",
            metadata={"openstack_uuid": vm_uuid},
        )


def get_secret_id_token(wrapped_secret_id) -> str:
    """
    Returns token for wrapped secret id
    """
    return wrapped_secret_id["wrap_info"]["token"]


def list_approle_secret_accessors(approle, vault_group) -> List[str]:
    """
    List secret accessor for a given AppRole
    """
    try:
        with VaultClient() as client:
            return client.auth.approle.list_secret_id_accessors(
                role_name=approle,
                mount_point=vault_group,
            )["data"]["keys"]
    except:
        return []


def get_secret_accessor_metadata(approle, vault_group, secret_accessor) -> dict:
    """
    Get metadata for a given AppRole
    """
    with VaultClient() as client:
        return client.auth.approle.read_secret_id_accessor(
            role_name=approle,
            secret_id_accessor=secret_accessor,
            mount_point=vault_group,
        )["data"]["metadata"]


def get_vm_secret_accessors(approle, vault_group, vm_uuid) -> List[str]:
    """
    Get secret accessors for the AppRole assocciated with a VM
    """
    secret_accessors = list_approle_secret_accessors(
        approle=approle, vault_group=vault_group
    )
    vm_secret_accessors = []
    for i in secret_accessors:
        if (
            get_secret_accessor_metadata(
                approle=approle, vault_group=vault_group, secret_accessor=i
            ).get("openstack_uuid")
            == vm_uuid
        ):
            vm_secret_accessors.append(i)
    return vm_secret_accessors


def revoke_secret_accessors(approle, vault_group, secret_accessors) -> None:
    """
    Revoke a list of secret accessors for a given AppRole
    """
    with VaultClient() as client:
        for i in secret_accessors:
            client.auth.approle.destroy_secret_id_accessor(
                role_name=approle, secret_id_accessor=i, mount_point=vault_group
            )
            logger.info("Revoked: " + i)
