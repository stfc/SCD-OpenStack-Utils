from lib.utils.csv_to_dataclass import separate_data
from unittest.mock import patch, mock_open


def test_separate_data():
    with patch("builtins.open", mock_open(read_data="mock_file_path")) as mock_file:
        separate_data("mock_file_path")
        mock_file.assert_called_once_with("mock_file_path")





