from dataclasses import dataclass
from typing import Optional


@dataclass
class Args:
    """
    The arguments related to Git operations.
    """

    target_dir: Optional[str]
    ssh_key_path: str
    push_to_github: bool
    make_image_public: bool = False
    os_version: str = "2004"

    # Set during runtime
    is_tmp_dir: bool = False
