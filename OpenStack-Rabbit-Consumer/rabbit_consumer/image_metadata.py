import dataclasses
import logging
from dataclasses import dataclass
from typing import Optional, Type, Mapping, Any

from mashumaro import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin, T


logger = logging.getLogger(__name__)


@dataclass
class ImageMetadata(DataClassDictMixin):
    """
    Deserialised metadata that is set on OpenStack images
    """

    AQ_ARCHETYPE: Optional[str] = None
    AQ_DOMAIN: Optional[str] = None

    AQ_PERSONALITY: Optional[str] = None
    AQ_OSVERSION: Optional[str] = None
    AQ_OS: Optional[str] = None

    @classmethod
    def __post_deserialize__(
        cls: Type[T], obj: "ImageMetadata"
    ) -> Optional["ImageMetadata"]:
        """
        Post de-serialisation hook to check for missing fields
        """
        fields = dataclasses.fields(obj)
        if not any(getattr(obj, f.name) for f in fields):
            # This doesn't have any fields set, so we can't validate it
            return None

        if not all(getattr(obj, f.name) for f in fields):
            logger.error(f"Missing data for on object {obj}")
            return None

        return obj
