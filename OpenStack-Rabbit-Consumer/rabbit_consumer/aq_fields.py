from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AqFields:
    """
    Holds fields that are commonly passed to Aquillon across the codebase
    """

    archetype: str
    hostnames: List[str]
    osname: Optional[str]
    osversion: Optional[str]
    personality: str
    project_id: str
