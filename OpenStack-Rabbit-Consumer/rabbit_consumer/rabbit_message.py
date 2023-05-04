from dataclasses import dataclass, field
from typing import Optional

from mashumaro import field_options
from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class MessageEventType(DataClassJSONMixin):
    """
    Parses a raw message from RabbitMQ to determine the event_type
    """

    event_type: str


@dataclass
class RabbitMeta(DataClassJSONMixin):
    """
    Deserialised custom VM metadata
    """

    machine_name: Optional[str] = field(
        metadata=field_options(alias="AQ_MACHINENAME"), default=None
    )


@dataclass
# pylint: disable=too-many-instance-attributes
class RabbitPayload(DataClassJSONMixin):
    """
    Deserialises the payload of a RabbitMQ message
    """

    fixed_ips: list[str]
    instance_id: str
    user_name: str
    image_name: str
    vm_name: str

    vcpus: int
    memory_mb: int
    vm_host: str = field(metadata=field_options(alias="host"))

    metadata: RabbitMeta


@dataclass
class RabbitMessage(DataClassJSONMixin):
    """
    Deserialised RabbitMQ message
    """

    event_type: str
    project_name: str = field(metadata=field_options(alias="_context_project_name"))
    project_id: str = field(metadata=field_options(alias="_context_project_id"))
    user_name: str = field(metadata=field_options(alias="_context_user_name"))
    payload: RabbitPayload
