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
    expected_version = semver.VersionInfo(major=1, minor=2, patch=3)
    output_file = tmp_path / "ubuntu-2004-kube-v1.2.3"
    output_file.touch()

    assert get_image_version(output_file) == expected_version


def test_get_image_version_missing_ubuntu(tmp_path):
    output_file = tmp_path / "rhel-8-kube-v1.2.3"
    output_file.touch()

    with pytest.raises(RuntimeError) as error:
        get_image_version(output_file)

    assert "Expected image filename to contain 'ubuntu'" in str(error.value)


def test_get_image_version_missing_kube(tmp_path):
    output_file = tmp_path / "ubuntu-2004-v1.2.3"
    output_file.touch()

    with pytest.raises(RuntimeError) as error:
        get_image_version(output_file)

    assert "Expected image filename to contain 'kube'" in str(error.value)


@patch("builder.image_ops.openstack")
def test_upload_image(mock_openstack, tmp_path):
    """
    Test that the upload_image function triggers Openstack correctly
    """
    details = ImageDetails(
        kube_version=semver.VersionInfo(major=1, minor=2, patch=3),
        os_version="2004",
        image_path=tmp_path / "example_image",
        is_public=False,
    )

    for visibility in [True, False]:
        expected = "public" if visibility else "private"

        mock_openstack.reset_mock()
        upload_output_image(details)

        mock_openstack.connect.assert_called_once_with("openstack")
        conn = mock_openstack.connect.return_value
        conn.image.create_image.assert_called_once_with(
            name="capi-ubuntu-2004-kube-v1.2.3",
            filename=details.image_path.as_posix(),
            disk_format="qcow2",
            container_format="bare",
            visibility="private",
        )


def test_push_new_image():
    """
    Test that the push_new_image function builds and
    pushes the correct image
    """
    image_path = NonCallableMock()
    args = NonCallableMock()

    with patch("builder.image_ops.get_image_version") as get_image_version, patch(
        "builder.image_ops.upload_output_image"
    ) as upload_output_image:

        image = push_new_image(image_path, args)

    get_image_version.assert_called_once_with(image_path)
    upload_output_image.assert_called_once_with(
        ImageDetails(
            kube_version=get_image_version.return_value,
            os_version=args.os_version,
            image_path=image_path,
            is_public=args.make_image_public,
        )
    )
    assert image == upload_output_image.return_value
