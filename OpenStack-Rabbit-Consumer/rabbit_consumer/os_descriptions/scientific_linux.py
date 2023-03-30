from dataclasses import dataclass

from rabbit_consumer.os_descriptions.base_os_descriptions import OsDescription


@dataclass
class ScientificLinux7(OsDescription):
    """
    Scientific Linux 7 OS description
    """

    os_identifiers = ["scientificlinux-7-aq"]
    aq_os_name = "sl"
    aq_os_version = "7x-x86_64"
    aq_default_personality = "nubesvms"


@dataclass
class ScientificLinux7NoGui(OsDescription):
    """
    Scientific Linux 7 OS description - No GUI
    """

    os_identifiers = ["scientificlinux-7-nogui"]
    aq_os_name = "sl"
    aq_os_version = "7x-x86_64"
    aq_default_personality = "nubes-unmanaged-nogui"


@dataclass
class ScientificLinux7Gui(OsDescription):
    """
    Scientific Linux 7 OS description - GUI
    """

    os_identifiers = ["scientificlinux-7-gui"]
    aq_os_name = "sl"
    aq_os_version = "7x-x86_64"
    aq_default_personality = "nubes-gui"
