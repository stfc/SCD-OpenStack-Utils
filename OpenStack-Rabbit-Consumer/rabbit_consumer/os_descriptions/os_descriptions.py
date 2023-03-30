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
    aq_default_personality: str = field(init=False)

    @classmethod
    def from_image_name(cls, image_name: str) -> "OsDescription":
        # This breaks the circular import, by loading subclasses
        # dynamically when we need them

        # noinspection PyUnresolvedReferences
        from . import centos, scientific_linux, rocky

        for subclass in cls.__subclasses__():
            for identifier in subclass.os_identifiers:
                if identifier.casefold() in image_name.casefold():
                    return subclass()
        raise ValueError(f"Could not find OS for image {image_name}")
