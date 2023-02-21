from pathlib import Path
from unittest.mock import patch, NonCallableMock

from main import main


def test_main(tmp_path):
    args = NonCallableMock()
    args.target_dir = tmp_path.as_posix()

    with patch("main.prepare_image_repo") as image_prep, patch(
        "main.build_image"
    ) as build_image, patch("main.push_new_image") as push_image:
        main(args)

    image_prep.assert_called_once_with(args)
    build_image.assert_called_once_with(args)
    push_image.assert_called_once_with(build_image.return_value, args)
