# TODO Push to GitHub with new tag
# TODO cleanup the temporary directory
import argparse
from pathlib import Path

from args import Args
from builder.git_steps import prepare_image_repo
from builder.image_ops import (
    get_image_details,
    get_existing_image_names,
    upload_output_image,
    archive_images,
)
from builder.packer import build_image
from openstack.image.v2.image import Image


def _parse_args() -> Args:
    parser = argparse.ArgumentParser(
        prog="CapiImageBuilder",
        description="Builds images for use with CAPI, publishes them to OpenStack"
        "and updates the repo on Github.",
    )

    parser.add_argument("ssh_key_path", help="The path to the SSH key to use.")
    parser.add_argument(
        "--target-dir",
        help="The directory to clone the repo to."
        "If not set this will use a temporary directory.",
    )
    parser.add_argument(
        "--push-to-github",
        action="store_true",
        help="Push the new image to Github. Default: False",
    )
    parser.add_argument(
        "--make-image-public",
        action="store_true",
        help="Make the new image public. Default: False",
    )
    parser.add_argument(
        "--openstack-cloud",
        default="openstack",
        help="The OpenStack cloud to upload the image to from clouds.yaml."
        " Default: openstack",
    )
    parser.add_argument(
        "--os-version",
        default="2004",
        help="The Ubuntu version to build. Default: 2004",
    )
    parser.add_argument(
        "--git-branch",
        default="master",
        help="The branch to build from. Default: master",
    )
    parser.add_argument(
        "--image-name",
        default=None,
        help="Overrides name of the image to build. Default: <Based on upstream K8s version>",
    )

    args = parser.parse_args()
    return Args(**vars(args))


def rotate_openstack_images(args: Args, image_path: Path) -> Image:
    """
    Rotates the OpenStack images, removing the oldest one
    and making the newest one public.
    """
    # Need to rotate images before we're allowed to upload another
    existing_images = get_existing_image_names(args.openstack_cloud)
    if not args.image_name:
        archive_images(existing_images, args.openstack_cloud)

    image_details = get_image_details(image_path, args)
    return upload_output_image(image_details, args)


def main(args: Args):
    """
    The main entry point for the program.
    Clones, merges and builds a new image then
    uploads it to OpenStack and (optionally) pushes the changes to Github.
    """
    prepare_image_repo(args)
    # Hardcode the Ubuntu version for now
    image_path = build_image(args)
    openstack_image = rotate_openstack_images(args, image_path)
    print(openstack_image)


if __name__ == "__main__":
    main(_parse_args())
