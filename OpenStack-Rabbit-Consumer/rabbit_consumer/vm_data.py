from dataclasses import dataclass
from typing import List, Optional


@dataclass
class VmData:
    """
    Holds fields that change between different virtual machines
    """

    hostnames: List[str]
    project_id: str
