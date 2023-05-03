import pytest

from rabbit_consumer.os_descriptions.os_descriptions import OsDescription


@pytest.mark.parametrize(
    "image_name",
    [
        "scientificlinux-7-aq",
        "ScientificLinux-7-aq",
        "scientificlinux-7-nogui",
        "scientificlinux-7-aq",
        "scientificlinux-7-gui",
        "warehoused-scientificlinux-7-aq-01-02-2023-17-00-43",
    ],
)
def test_sl7(image_name):
    """
    Test that the function returns the correct OS description for SL7 images
    """
    os = OsDescription.from_image_name(image_name)
    assert isinstance(os, OsDescription)
    assert os.aq_os_name == "sl"
    assert os.aq_os_version == "7x-x86_64"


@pytest.mark.parametrize(
    "image_name",
    [
        "centos-7-aq",
        "warehoused-centos-7-aq-01-02-2023-17-00-43",
    ],
)
def test_centos7(image_name):
    """
    Test that the function returns the correct OS description for CentOS 7 images
    """
    os = OsDescription.from_image_name(image_name)
    assert isinstance(os, OsDescription)
    assert os.aq_os_name == "centos"
    assert os.aq_os_version == "7x-x86_64"


@pytest.mark.parametrize(
    "image_name",
    [
        "rocky-8-aq",
        "Rocky-8-aq",
        "rocky-8-nogui",
        "rocky-8-aq",
        "rocky-8-gui",
        "warehoused-rocky-8-aq-01-02-2023-17-00-43",
    ],
)
def test_rocky8(image_name):
    """
    Test that the function returns the correct OS description for Rocky 8 images
    """
    os = OsDescription.from_image_name(image_name)
    assert isinstance(os, OsDescription)
    assert os.aq_os_name == "rocky"
    assert os.aq_os_version == "8x-x86_64"


@pytest.mark.parametrize(
    "image_name",
    [
        "rocky-9",
        "Rocky-9",
        "rocky-9-nogui",
        "rocky-9-aq",
        "rocky-9-gui",
        "warehoused-rocky-9-aq-01-02-2023-17-00-43",
    ],
)
def test_rocky9(image_name):
    """
    Test that the function returns the correct OS description for Rocky 9 images
    """
    os = OsDescription.from_image_name(image_name)
    assert isinstance(os, OsDescription)
    assert os.aq_os_name == "rocky"
    assert os.aq_os_version == "9x-x86_64"


@pytest.mark.parametrize(
    "image_name",
    [
        "scientificlinux-7-aq",
        "centos-7-aq",
        "rocky-8-aq",
    ],
)
def test_aq_based_images(image_name):
    """
    Checks the following images use the nubesvms personality
    by default
    """
    os = OsDescription.from_image_name(image_name)
    assert os.aq_default_personality == "nubesvms"


@pytest.mark.parametrize("image_name", ["scientificlinux-7-nogui", "rocky-8-nogui"])
def test_nogui_based_images(image_name):
    """
    Checks the following images use the nubes-unmanaged-nogui personality
    by default
    """
    os = OsDescription.from_image_name(image_name)
    assert os.aq_default_personality == "nubes-unmanaged-nogui"


@pytest.mark.parametrize("image_name", ["scientificlinux-7-gui", "rocky-8-gui"])
def test_gui_based_images(image_name):
    """
    Checks the following images use the nubes-gui personality
    by default
    """
    os = OsDescription.from_image_name(image_name)
    assert os.aq_default_personality == "nubes-gui"


@pytest.mark.parametrize(
    "image_name", ["unknown", "ubuntu", "capi", "fedora", "custom_image"]
)
def test_unknown(image_name):
    """
    Test that the function raises a ValueError when the image name is not recognized
    """
    with pytest.raises(ValueError):
        OsDescription.from_image_name(image_name)
