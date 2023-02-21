# TODO Push to GitHub with new tag
# TODO cleanup the temporary directory
import argparse

from builder.args import Args
from builder.git_steps import prepare_image_repo
from builder.image_ops import push_new_image
from builder.packer import build_image


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
        "--make_image_public",
        action="store_true",
        help="Make the new image public. Default: False",
    )
    parser.add_argument(
        "--os_version",
        default="2004",
        help="The Ubuntu version to build. Default: 2004",
    )

    args = parser.parse_args()
    return Args(**vars(args))


def main(args: Args):
    prepare_image_repo(args)
    # Hardcode the Ubuntu version for now
    image_path = build_image(args)
    openstack_image = push_new_image(image_path, args)
    print(openstack_image)


if __name__ == "__main__":
    main(_parse_args())
