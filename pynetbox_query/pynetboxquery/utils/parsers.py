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
            title="Actions",
            description="Valid Subcommands:\ncreate_devices\nvalidate_data_fields_in_netbox",
            dest="subparsers",
        )
        self._create_parser(subparsers, parent_parser)
        self._validate_parser(subparsers, parent_parser)
        return main_parser.parse_args()

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

    @staticmethod
    def _create_parser(subparsers, parent_parser):
        subparsers.add_parser(
            "create_devices",
            description="Create devices in Netbox from a file.",
            usage="pynetboxquery create_devices <filepath> <url> <token> <options>",
            parents=[parent_parser],
            aliases=["create"],
        )

    @staticmethod
    def _validate_parser(subparsers, parent_parser):
        parser_validate_data_fields_in_netbox = subparsers.add_parser(
            "validate_data_fields_in_netbox",
            description="Check data fields values in Netbox from a file.",
            usage="pynetboxquery validate_data_fields_in_netbox <filepath> <url> <token> <fields=[]>",
            parents=[parent_parser],
            aliases=["validate"],
        )
        parser_validate_data_fields_in_netbox.add_argument(
            "fields", help="The fields to check in Netbox.", nargs="*"
        )
        parser_validate_data_fields_in_netbox.add_argument(
            "--short",
            type=bool,
            help="To include all results or only bad results from Netbox.",
            dest="TRUE/FALSE",
        )
