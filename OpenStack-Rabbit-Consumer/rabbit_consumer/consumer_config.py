import os
from dataclasses import dataclass, field
from functools import partial


@dataclass
class _AqFields:
    aq_archetype: str = field(default_factory=partial(os.getenv, "AQ_ARCHETYPE"))
    aq_domain: str = field(default_factory=partial(os.getenv, "AQ_DOMAIN"))
    aq_personality: str = field(default_factory=partial(os.getenv, "AQ_PERSONALITY"))
    aq_prefix: str = field(default_factory=partial(os.getenv, "AQ_PREFIX"))
    aq_url: str = field(default_factory=partial(os.getenv, "AQ_URL"))


@dataclass
class _OpenstackFields:
    openstack_auth_url: str = field(
        default_factory=partial(os.getenv, "OPENSTACK_AUTH_URL")
    )
    openstack_ca_cert: str = field(
        default_factory=partial(os.getenv, "OPENSTACK_CA_CERT")
    )
    openstack_compute_url: str = field(
        default_factory=partial(os.getenv, "OPENSTACK_COMPUTE_URL")
    )
    openstack_domain_name: str = field(
        default_factory=partial(os.getenv, "OPENSTACK_DOMAIN_NAME")
    )
    openstack_project_id: str = field(
        default_factory=partial(os.getenv, "OPENSTACK_PROJECT_ID")
    )
    openstack_username: str = field(
        default_factory=partial(os.getenv, "OPENSTACK_USERNAME")
    )
    openstack_password: str = field(
        default_factory=partial(os.getenv, "OPENSTACK_PASSWORD")
    )


@dataclass
class _RabbitFields:
    rabbit_host: str = field(default_factory=partial(os.getenv, "RABBIT_HOST", None))
    rabbit_port: str = field(default_factory=partial(os.getenv, "RABBIT_PORT", None))
    rabbit_username: str = field(
        default_factory=partial(os.getenv, "RABBIT_USERNAME", None)
    )
    rabbit_password: str = field(
        default_factory=partial(os.getenv, "RABBIT_PASSWORD", None)
    )


@dataclass
class ConsumerConfig(_AqFields, _OpenstackFields, _RabbitFields):
    """
    Mix-in class for all known config elements
    """

    pass
