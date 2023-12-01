# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
from pynetboxquery.utils.parsers import Parsers
from pynetboxquery.netbox_api.validate_data import ValidateData
from pynetboxquery.utils.read_utils.read_file import ReadFile
from pynetboxquery.netbox_api.netbox_connect import api_object
from pynetboxquery.user_methods.abstract_user_method import AbstractUserMethod


class Main(AbstractUserMethod):
    """
    This class contains the run method to run the user script.
    """

    @staticmethod
    def _run(url: str, token: str, file_path: str, **kwargs):
        """
        This function does the following:
        Reads the file from the file path.
        Creates a Pynetbox Api Object with the users credentials.
        Validates all the fields specified by the user
        :param url: The Netbox URL.
        :param token: The users Netbox api token.
        :param file_path: The file_path.
        """
        device_list = ReadFile().read_file(file_path, **kwargs)
        api = api_object(url, token)
        ValidateData().validate_data(device_list, api, kwargs["fields"])

    def _subparser(self):
        """
        This function creates the subparser for this user script inheriting the parent parser arguments.
        It also adds an argument to collect the fields specified in the command line.
        """
        parent_parser, main_parser, subparsers = Parsers().arg_parser()
        parser_validate_data_fields_in_netbox = subparsers.add_parser(
            "validate_data_fields_in_netbox",
            description="Check data fields values in Netbox from a file.",
            usage="pynetboxquery validate_data_fields_in_netbox <filepath> <url> <token> <fields=[]>",
            parents=[parent_parser],
            aliases=self.aliases(),
        )
        parser_validate_data_fields_in_netbox.add_argument(
            "fields", help="The fields to check in Netbox.", nargs="*"
        )
        return main_parser

    @staticmethod
    def aliases():
        """
        This function returns a list of aliases the script should be callable by.
        """
        return ["validate", "validate_data_fields_in_netbox"]
