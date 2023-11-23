from dataclasses import asdict
from unittest.mock import patch
from pytest import raises
from pynetboxquery.utils.read_utils.read_abc import ReadAbstractBase


class StubAbstractBase(ReadAbstractBase):

    def read(self):
        pass

    @staticmethod
    def _validate(kwargs):
        pass


@patch("pynetboxquery.utils.read_utils.read_abc.Path")
def test_check_file_path(mock_path):
    StubAbstractBase("mock_file_path")._check_file_path("mock_file_path")
    mock_path.assert_called_with("mock_file_path")
    mock_path.return_value.exists.assert_called()


@patch("pynetboxquery.utils.read_utils.read_abc.Path")
def test_check_file_path_error(mock_path):
    mock_path.return_value.exists.return_value = False
    with raises(FileNotFoundError):
        StubAbstractBase("mock_file_path")._check_file_path("mock_file_path")
    mock_path.assert_called_with("mock_file_path")
    mock_path.return_value.exists.assert_called()


def test_dict_to_dataclass(mock_device):
    with patch("pynetboxquery.utils.read_utils.read_abc.Path"):
        mock_dictionary = [asdict(mock_device)]
        res = StubAbstractBase("mock_file_path")._dict_to_dataclass(mock_dictionary)
        assert res == [mock_device]
