import argparse


def arg_parser():
    """
    This function creates a parser object and adds 3 arguments to it.
    This allows users to run the python file with arguments. Like a script.
    """
    parser = argparse.ArgumentParser(
        description="Create devices in Netbox from CSV files.",
        usage="python csv_to_netbox.py url token file_path",
    )
    parser.add_argument("url", help="The Netbox URL.")
    parser.add_argument("token", help="Your Netbox Token.")
    parser.add_argument("file_path", help="Your file path to csv files.")
    return parser.parse_args()