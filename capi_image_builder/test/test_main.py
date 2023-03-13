from unittest.mock import patch, NonCallableMock

from main import main, rotate_openstack_images


def test_main(tmp_path):
    """
    Tests the main steps, which consist of very high level goals.
    """
    args = NonCallableMock()
    args.target_dir = tmp_path.as_posix()

    with patch("main.prepare_image_repo") as image_prep, patch(
        "main.build_image"
    ) as build_image, patch("main.rotate_openstack_images") as image_rotate:
        main(args)

    image_prep.assert_called_once_with(args)
    build_image.assert_called_once_with(args)
    image_rotate.assert_called_once_with(args, build_image.return_value)


@patch("main.get_image_details")
@patch("main.get_existing_image_names")
@patch("main.upload_output_image")
@patch("main.archive_images")
def test_rotate_openstack_images(
    archive_images,
    upload_output_image,
    get_existing_image_names,
    get_image_details,
    tmp_path,
):
    """
    Tests the rotation of images in openstack
    """
    args = NonCallableMock()
    args.image_name = None
    new_image = rotate_openstack_images(args, tmp_path)

    get_image_details.assert_called_once_with(tmp_path, args)
    image_details = get_image_details.return_value

    get_existing_image_names.assert_called_once_with(args.openstack_cloud)
    upload_output_image.assert_called_once_with(image_details, args)
    archive_images.assert_called_once_with(
        get_existing_image_names.return_value, args.openstack_cloud
    )

    assert new_image == upload_output_image.return_value


@patch("main.upload_output_image")
@patch("main.archive_images")
def test_rotate_openstack_images_custom_name(
    archive_images, upload_output_image, tmp_path
):
    """
    Tests the rotation of images in openstack is
    suppressed when a custom image name is provided
    """
    args = NonCallableMock()
    args.image_name = "custom-image-name"

    with patch("main.get_image_details"), patch("main.get_existing_image_names"):
        new_image = rotate_openstack_images(args, tmp_path)

    upload_output_image.assert_called_once()
    archive_images.assert_not_called()

    assert new_image == upload_output_image.return_value
