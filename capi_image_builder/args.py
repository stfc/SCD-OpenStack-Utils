from dataclasses import dataclass
from typing import Optional


@dataclass
class Args:
    """
    The arguments related to Git operations.
    """

    ssh_key_path: str
    push_to_github: bool

    openstack_cloud: str
    image_name: Optional[str] = None
    make_image_public: bool = False

    # Sane defaults
    git_branch: str = "master"
    os_version: str = "2004"
    target_dir: Optional[str] = None

    # Set during runtime
    is_tmp_dir: bool = False
