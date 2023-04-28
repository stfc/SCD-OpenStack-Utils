from dataclasses import dataclass

from rabbit_consumer.rabbit_message import RabbitMessage


@dataclass
class VmData:
    """
    Holds fields that change between different virtual machines
    """

    project_id: str
    virtual_machine_id: str

    @staticmethod
    def from_message(message: RabbitMessage) -> "VmData":
        return VmData(
            project_id=message.project_id,
            virtual_machine_id=message.payload.instance_id,
        )
