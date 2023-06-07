import logging
from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, field_options

logger = logging.getLogger(__name__)


@dataclass
class ImageMetadata(DataClassDictMixin):
    """
    Deserialised metadata that is set on OpenStack images
    """

    aq_archetype: str = field(metadata=field_options(alias="AQ_ARCHETYPE"))
    aq_domain: str = field(metadata=field_options(alias="AQ_DOMAIN"))

    aq_personality: str = field(metadata=field_options(alias="AQ_PERSONALITY"))
    aq_os_version: str = field(metadata=field_options(alias="AQ_OSVERSION"))
    aq_os: str = field(metadata=field_options(alias="AQ_OS"))
