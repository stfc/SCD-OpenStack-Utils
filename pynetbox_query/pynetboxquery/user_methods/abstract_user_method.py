from abc import ABC, abstractmethod
from typing import List, Dict
from argparse import ArgumentParser


class AbstractUserMethod(ABC):
    """
    This Abstract class provides a template for user methods.
    """

    def _collect_args(self) -> Dict:
        """
        This method collects the arguments from the subparser into a dictionary of kwargs.
        :return: Dictionary of kwargs.
        """
        main_parser = self._subparser()
        args = main_parser.parse_args()
        kwargs = vars(args)
        return kwargs

    @abstractmethod
    def _subparser(self) -> ArgumentParser:
        """
        This method creates a subparser with specific arguments to the user method.
        :return: Returns the main parser that should contain the subparser information.
        """

    @staticmethod
    @abstractmethod
    def aliases() -> List[str]:
        """Returns the aliases viable for this user_method."""

    def main(self):
        """
        This method gets the arguments and calls the run method with them.
        """
        kwargs = self._collect_args()
        self._run(**kwargs)

    @staticmethod
    @abstractmethod
    def _run(url: str, token: str, file_path: str, **kwargs):
        """
        This the main method in the user script. It contains all calls needed to perform the action.
        """
