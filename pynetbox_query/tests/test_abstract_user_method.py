from argparse import ArgumentParser
from typing import List
from unittest.mock import patch
from pytest import fixture
from pynetboxquery.user_methods.abstract_user_method import AbstractUserMethod


@fixture(name="instance")
def instance_fixture():
    """
    This fixture returns the Stub class to be tested.
    """
    return StubAbstractUserMethod()


class StubAbstractUserMethod(AbstractUserMethod):
    """
    This class provides a Stub version of the AbstractUserMethod class.
    So we do not have to patch all the abstract methods.
    """

    def _subparser(self) -> ArgumentParser:
        """Placeholder Method."""

    @staticmethod
    def aliases() -> List[str]:
        """Placeholder Method."""

    @staticmethod
    def _run(url: str, token: str, file_path: str, **kwargs):
        """Placeholder Method."""


@patch(
    "pynetboxquery.user_methods.abstract_user_method.AbstractUserMethod._collect_kwargs"
)
def test_main(mock_collect_kwargs, instance):
    """
    This test ensures the collect kwargs method is called.
    We do not need to assert that ._run is called as it is an abstract method.
    """
    mock_collect_kwargs.return_value = {
        "url": "mock_url",
        "token": "mock_token",
        "file_path": "mock_file_path",
    }
    instance.main()
    mock_collect_kwargs.assert_called_once()
