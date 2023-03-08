from unittest.mock import patch, NonCallableMock, Mock, call

import pytest
import semver

from builder.image_ops import (
    get_image_version,
    upload_output_image,
    ImageDetails,
    get_existing_image_names,
    archive_images,
    get_image_details,
)


def test_get_image_version(tmp_path):
    """
    Tests get image version returns the correct semver
    based on the filename.
    """
    expected_version = semver.VersionInfo(major=1, minor=2, patch=3)
    output_file = tmp_path / "ubuntu-2004-kube-v1.2.3"
    output_file.touch()

    assert get_image_version(output_file) == expected_version


def test_get_image_version_missing_ubuntu(tmp_path):
    """
    Tests get image version raises an error if the filename
    does not contain 'ubuntu'.
    """
    output_file = tmp_path / "rhel-8-kube-v1.2.3"
    output_file.touch()

    with pytest.raises(RuntimeError) as error:
        get_image_version(output_file)

    assert "Expected image filename to contain 'ubuntu'" in str(error.value)


def test_get_image_version_missing_kube(tmp_path):
    """
    Tests get image version raises an error if the filename
    does not contain 'kube'.
    """
    output_file = tmp_path / "ubuntu-2004-v1.2.3"
    output_file.touch()

    with pytest.raises(RuntimeError) as error:
        get_image_version(output_file)

    assert "Expected image filename to contain 'kube'" in str(error.value)


def test_get_image_version_missing_trailing_version(tmp_path):
    """
    Tests get image version raises an error if the filename
    does not contain a trailing semantic version.
    """
    output_file = tmp_path / "ubuntu-2004-kube-v1.2"
    output_file.touch()

    with pytest.raises(ValueError) as error:
        get_image_version(output_file)

    assert "1.2 is not valid SemVer string" in str(error.value)


def test_get_image_name():
    """
    Tests that the get_image_name function returns the correct name
    """
    details = ImageDetails(
        kube_version=semver.VersionInfo(major=1, minor=2, patch=3),
        os_version="2004",
        image_path=NonCallableMock(),
        is_public=True,
    )
    assert details.get_image_name() == "capi-ubuntu-2004-kube-v1.2.3"


@patch("builder.image_ops.openstack")
def test_upload_image(mock_openstack, tmp_path):
    """
    Test that the upload_image function triggers Openstack correctly
    """
    for visibility in [True, False]:
        details = ImageDetails(
            kube_version=semver.VersionInfo(major=1, minor=2, patch=3),
            os_version="2004",
            image_path=tmp_path / "example_image",
            is_public=visibility,
        )
        expected = "public" if visibility else "private"

        mock_openstack.reset_mock()
        mock_cloud = NonCallableMock()
        upload_output_image(details, mock_cloud)

        mock_openstack.connect.assert_called_once_with(mock_cloud)
        conn = mock_openstack.connect.return_value
        conn.image.create_image.assert_called_once_with(
            name="capi-ubuntu-2004-kube-v1.2.3",
            filename=details.image_path.as_posix(),
            disk_format="qcow2",
            container_format="bare",
            visibility=expected,
        )


def test_get_image_details():
    """
    Test that the get_image_details function returns
    the correct ImageDetails object
    """
    image_path = NonCallableMock()
    args = NonCallableMock()

    with patch("builder.image_ops.get_image_version") as mock_get_image_version:
        details = get_image_details(image_path, args)

    mock_get_image_version.assert_called_once_with(image_path)
    assert details == ImageDetails(
        kube_version=mock_get_image_version.return_value,
        os_version=args.os_version,
        image_path=image_path,
        is_public=args.make_image_public,
    )


def test_get_existing_image_names():
    """
    Test that the check_existing_image function returns
    if an image exists with the target name
    """
    expected_return = [NonCallableMock(), NonCallableMock()]
    image_details = Mock()
    expected_cloud_account = "test_cloud_account"
    with patch("builder.image_ops.openstack") as mock_openstack:
        images_api = mock_openstack.connect.return_value.image.images
        images_api.return_value = expected_return
        returned = get_existing_image_names(
            image_details, clouds_account=expected_cloud_account
        )

    mock_openstack.connect.assert_called_once_with(expected_cloud_account)
    images_api.assert_called_once_with(name=image_details.get_image_name())
    assert returned == expected_return


def test_archive_images_single_image():
    """
    Test that the archive_images function returns
    if an image exists with the target name
    """
    images = [NonCallableMock()]
    expected_cloud_account = "test_cloud_account"

    with patch("builder.image_ops.openstack") as mock_openstack, patch(
        "builder.image_ops.datetime"
    ) as mock_datetime:
        archive_images(images, clouds_account=expected_cloud_account)

    mock_openstack.connect.assert_called_once_with(expected_cloud_account)
    update_api = mock_openstack.connect.return_value.image.update_image

    # Check YYYY-MM-DD format was used
    mock_datetime.utcnow.assert_called_once()
    mock_datetime.utcnow.return_value.strftime.assert_called_once_with("%Y-%m-%d")
    expected_date = mock_datetime.utcnow.return_value.strftime.return_value

    update_api.assert_has_calls(
        [
            call(images[0], deactivate=True),
            call(images[0], name=f"warehoused-{images[0].name}-{expected_date}"),
        ]
    )


def test_archive_images_multiple_images():
    """
    Test that the archive_images function returns
    if an image exists with the target name
    """
    images = [NonCallableMock(), NonCallableMock()]
    expected_cloud_account = "test_cloud_account"

    with patch("builder.image_ops.openstack") as mock_openstack, patch(
        "builder.image_ops.datetime"
    ) as mock_datetime:
        archive_images(images, clouds_account=expected_cloud_account)

    mock_openstack.connect.assert_called_once_with(expected_cloud_account)
    update_api = mock_openstack.connect.return_value.image.update_image

    expected_date = mock_datetime.utcnow.return_value.strftime.return_value

    expected_calls = [call(i, deactivate=True) for i in images]
    expected_calls.extend(
        [
            call(i, name=f"warehoused-{i.name}-{expected_date}-{num}")
            for num, i in enumerate(images)
        ]
    )
    update_api.assert_has_calls(expected_calls, any_order=True)
