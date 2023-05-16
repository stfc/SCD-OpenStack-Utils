import dataclasses
import logging
from dataclasses import dataclass, field
from typing import Optional, Type

from mashumaro import DataClassDictMixin, field_options
from mashumaro.mixins.json import T

logger = logging.getLogger(__name__)


@dataclass
class ImageMetadata(DataClassDictMixin):
    """
    Deserialised metadata that is set on OpenStack images
    """

    aq_archetype: Optional[str] = field(metadata=field_options(alias="AQ_ARCHETYPE"))
    aq_domain: Optional[str] = field(metadata=field_options(alias="AQ_DOMAIN"))

    aq_personality: Optional[str] = field(
        metadata=field_options(alias="AQ_PERSONALITY")
    )
    aq_os_version: Optional[str] = field(metadata=field_options(alias="AQ_OSVERSION"))
    aq_os: Optional[str] = field(metadata=field_options(alias="AQ_OS"))

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
            logger.error("Missing data for on object %s", obj)
            return None

        return obj
