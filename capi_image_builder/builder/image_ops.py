from dataclasses import dataclass
from pathlib import Path

import openstack.connection
import semver
from openstack.image.v2.image import Image

from args import Args


def get_image_version(output_file: Path) -> semver.VersionInfo:
    """
    Gets the Kubectl version based on the filename
    """
    filename = output_file.name
    if "ubuntu" not in filename:
        raise RuntimeError("Expected image filename to contain 'ubuntu'.")

    if "kube" not in filename:
        raise RuntimeError("Expected image filename to contain 'kube'.")

    # Split the filename on "kube-v" to get the version number after
    split_name = filename.split("kube-v")
    if len(split_name) != 2:
        raise RuntimeError("Expected image filename to contain 'kube-v'.")

    version = split_name[1]
    return semver.VersionInfo.parse(version)


@dataclass
class ImageDetails:
    """
    Holds details of a newly built image
    """

    kube_version: semver.VersionInfo
    image_path: Path
    is_public: bool
    os_version: str

    def get_image_name(self) -> str:
        """
        Returns the name of the image based on the image details
        """
        return f"capi-ubuntu-{self.os_version}-kube-v{self.kube_version}"


def upload_output_image(image_details: ImageDetails, clouds_account: str) -> Image:
    """
    Uploads a given image to Openstack and returns the resulting image object
    provided by the Openstack SDK
    """
    visibility = "public" if image_details.is_public else "private"
    print(f"Uploading image {image_details.image_path} to Openstack")
    print(f"Image visibility: {visibility}")

    conn = openstack.connect(clouds_account)
    return conn.image.create_image(
        name=image_details.get_image_name(),
        filename=image_details.image_path.as_posix(),
        disk_format="qcow2",
        container_format="bare",
        visibility=visibility,
    )


def push_new_image(image_path: Path, args: Args) -> Image:
    """
    Build a new image using Packer and returns the resulting image name
    """
    image_version = get_image_version(image_path)
    image_details = ImageDetails(
        kube_version=image_version,
        image_path=image_path,
        is_public=args.make_image_public,
        os_version=args.os_version,
    )
    return upload_output_image(image_details, args.openstack_cloud)
