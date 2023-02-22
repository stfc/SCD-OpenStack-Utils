from unittest.mock import patch, NonCallableMock

import pytest
import semver

from builder.image_ops import (
    get_image_version,
    upload_output_image,
    ImageDetails,
    push_new_image,
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


def test_push_new_image():
    """
    Test that the push_new_image function builds and
    pushes the correct image
    """
    image_path = NonCallableMock()
    args = NonCallableMock()

    with patch("builder.image_ops.get_image_version") as mock_get_image_version, patch(
        "builder.image_ops.upload_output_image"
    ) as mock_upload_image:
        image = push_new_image(image_path, args)

    mock_get_image_version.assert_called_once_with(image_path)
    mock_upload_image.assert_called_once_with(
        ImageDetails(
            kube_version=mock_get_image_version.return_value,
            os_version=args.os_version,
            image_path=image_path,
            is_public=args.make_image_public,
        ),
        args.openstack_cloud,
    )
    assert image == mock_upload_image.return_value
