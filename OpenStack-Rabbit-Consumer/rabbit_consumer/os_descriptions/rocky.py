from dataclasses import dataclass

from rabbit_consumer.os_descriptions.os_descriptions import OsDescription


@dataclass
class Rocky8(OsDescription):
    """
    Rocky 8 OS description
    """

    os_identifiers = ["rocky-8-aq"]
    aq_os_name = "rocky"
    aq_os_version = "8x-x86_64"
    aq_default_personality = "nubesvms"


@dataclass
class Rocky8NoGui(OsDescription):
    """
    Rocky 8 OS description - No GUI
    """

    os_identifiers = ["rocky-8-nogui"]
    aq_os_name = "rocky"
    aq_os_version = "8x-x86_64"
    aq_default_personality = "nubes-unmanaged-nogui"


@dataclass
class Rocky8Gui(OsDescription):
    """
    Rocky 8 OS description - GUI
    """

    os_identifiers = ["rocky-8-gui"]
    aq_os_name = "rocky"
    aq_os_version = "8x-x86_64"
    aq_default_personality = "nubes-gui"


@dataclass
class Rocky9(OsDescription):
    """
    Rocky 9 OS description
    """

    os_identifiers = ["rocky-9"]
    aq_os_name = "rocky"
    aq_os_version = "9x-x86_64"
    aq_default_personality = "nubesvms"
