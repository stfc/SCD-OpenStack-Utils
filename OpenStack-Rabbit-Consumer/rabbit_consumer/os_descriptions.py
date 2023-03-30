import abc
from dataclasses import dataclass, field


@dataclass
class OsDescription(abc.ABC):
    """
    Abstract base class for OS descriptions
    """

    os_identifiers: list[str] = field(init=False)
    aq_os_name: str = field(init=False)
    aq_os_version: str = field(init=False)

    @classmethod
    def from_image_name(cls, image_name: str) -> "OsDescription":
        for subclass in cls.__subclasses__():
            for identifier in subclass.os_identifiers:
                if identifier.casefold() in image_name.casefold():
                    return subclass()
        raise ValueError(f"Could not find OS for image {image_name}")


@dataclass
class ScientificLinux7(OsDescription):
    """
    Scientific Linux 7 OS description
    """

    os_identifiers = ["scientificlinux-7"]
    aq_os_name = "sl"
    aq_os_version = "7x-x86_64"


@dataclass
class Centos7(OsDescription):
    """
    Centos 7 OS description
    """

    os_identifiers = ["centos-7"]
    aq_os_name = "centos"
    aq_os_version = "7x-x86_64"


@dataclass
class Rocky8(OsDescription):
    """
    Rocky 8 OS description
    """

    os_identifiers = ["rocky-8", "rocky8"]
    aq_os_name = "rocky"
    aq_os_version = "8x-x86_64"


@dataclass
class Rocky9(OsDescription):
    """
    Rocky 9 OS description
    """

    os_identifiers = ["rocky-9", "rocky9"]
    aq_os_name = "rocky"
    aq_os_version = "9x-x86_64"
