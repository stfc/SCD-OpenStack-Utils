from dataclasses import dataclass

from rabbit_consumer.os_descriptions.base_os_descriptions import OsDescription


@dataclass
class Centos7(OsDescription):
    """
    Centos 7 OS description
    """

    os_identifiers = ["centos-7-aq"]
    aq_os_name = "centos"
    aq_os_version = "7x-x86_64"
    aq_default_personality = "nubesvms"
