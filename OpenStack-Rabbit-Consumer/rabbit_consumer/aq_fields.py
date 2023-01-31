from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AqFields:
    archetype: str
    hostnames: List[str]
    osname: Optional[str]
    osversion: Optional[str]
    personality: str
    project_id: str
