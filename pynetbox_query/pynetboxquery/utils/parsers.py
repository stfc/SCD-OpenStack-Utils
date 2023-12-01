# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
import argparse


# Disabling this Pylint warning as it's irrelevant.
# pylint: disable = R0903
class Parsers:
    """
    This class contains the argparse methods for different commands.
    """

    def arg_parser(self):
        """
        This function creates a parser object and adds 3 arguments to it.
        This allows users to run the python file with arguments. Like a script.
        """

        parent_parser = self._parent_parser()
        main_parser = argparse.ArgumentParser(
            description="The main command. This cannot be run standalone and requires a subcommand to be provided.",
            usage="pynetboxquery [command] [filepath] [url] [token] [kwargs]",
        )
        subparsers = main_parser.add_subparsers(
            dest="subparsers",
        )

        return parent_parser, main_parser, subparsers

    @staticmethod
    def _parent_parser():
        parent_parser = argparse.ArgumentParser(add_help=False)
        parent_parser.add_argument("url", help="The Netbox URL.")
        parent_parser.add_argument("token", help="Your Netbox Token.")
        parent_parser.add_argument("file_path", help="Your file path to csv files.")
        parent_parser.add_argument(
            "--delimiter", help="The separator in the text file."
        )
        parent_parser.add_argument(
            "--sheet-name", help="The sheet in the Excel Workbook to read from."
        )
        return parent_parser
