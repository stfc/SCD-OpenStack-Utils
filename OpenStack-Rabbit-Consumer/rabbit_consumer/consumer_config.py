import os
from dataclasses import dataclass, field
from functools import partial


@dataclass
class _AqFields:
    """
    Dataclass for all Aquilon config elements. These are pulled from
    environment variables.
    """

    aq_prefix: str = field(default_factory=partial(os.getenv, "AQ_PREFIX"))
    aq_url: str = field(default_factory=partial(os.getenv, "AQ_URL"))


@dataclass
class _OpenstackFields:
    """
    Dataclass for all Openstack config elements. These are pulled from
    environment variables.
    """

    openstack_auth_url: str = field(
        default_factory=partial(os.getenv, "OPENSTACK_AUTH_URL")
    )
    openstack_compute_url: str = field(
        default_factory=partial(os.getenv, "OPENSTACK_COMPUTE_URL")
    )
    openstack_username: str = field(
        default_factory=partial(os.getenv, "OPENSTACK_USERNAME")
    )
    openstack_password: str = field(
        default_factory=partial(os.getenv, "OPENSTACK_PASSWORD")
    )


@dataclass
class _RabbitFields:
    """
    Dataclass for all RabbitMQ config elements. These are pulled from
    environment variables.
    """

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
