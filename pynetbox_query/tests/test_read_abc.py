from dataclasses import asdict
from unittest.mock import patch
from pytest import raises
from pynetboxquery.utils.read_utils.read_abc import ReadAbstractBase

# pylint: disable = R0903
class StubAbstractBase(ReadAbstractBase):
    """
    This class provides a Stub version of the ReadAbstractBase class.
    So we do not have to patch all the abstract methods.
    """
    def read(self):
        """Placeholder method."""

    @staticmethod
    def _validate(kwargs):
        """Placeholder method."""


@patch("pynetboxquery.utils.read_utils.read_abc.Path")
def test_check_file_path(mock_path):
    """
    This test ensures the _check_file_path method is called.
    """
    StubAbstractBase("mock_file_path")._check_file_path("mock_file_path")
    mock_path.assert_called_with("mock_file_path")
    mock_path.return_value.exists.assert_called()


@patch("pynetboxquery.utils.read_utils.read_abc.Path")
def test_check_file_path_error(mock_path):
    """
    This test ensures the _check_file_path method is called and raises an error.
    """
    mock_path.return_value.exists.return_value = False
    with raises(FileNotFoundError):
        StubAbstractBase("mock_file_path")._check_file_path("mock_file_path")
    mock_path.assert_called_with("mock_file_path")
    mock_path.return_value.exists.assert_called()


def test_dict_to_dataclass(mock_device):
    """
    This test ensures that the method _dict_to_dataclass returns the right list of devices.
    """
    with patch("pynetboxquery.utils.read_utils.read_abc.Path"):
        mock_dictionary = [asdict(mock_device)]
        res = StubAbstractBase("mock_file_path")._dict_to_dataclass(mock_dictionary)
        assert res == [mock_device]
