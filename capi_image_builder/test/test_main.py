from unittest.mock import patch, NonCallableMock

from main import main


@patch("main.prepare_image_repo")
def test_main(image_prep):
    args = NonCallableMock()
    main(args)

    image_prep.assert_called_once_with(args)
