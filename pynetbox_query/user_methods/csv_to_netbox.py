import sys
from pynetbox_query.argparser import arg_parser
from pynetbox_query.top_level_methods import TopLevelMethods


def do_csv_to_netbox(args) -> bool:
    """
    This function calls the methods from CsvToNetbox class.
    :param args: The arguments from argparse. Supplied when the user runs the file from CLI.
    :return: Returns bool if devices where created or not.
    """
    methods = TopLevelMethods(url=args.url, token=args.token)
    methods.check_file_path(args.file_path)
    device_list = methods.read_csv(args.file_path)
    methods.validate_devices(device_list)
    methods.validate_device_types(device_list)
    converted_device_list = methods.query_data(device_list)
    result = methods.send_data(converted_device_list)
    return result


def main():
    """
    This function calls the necessary functions to call all other methods.
    """
    sys.stdout.write("Starting...")
    arguments = arg_parser()
    do_csv_to_netbox(arguments)
    sys.stdout.write("Finished.")


if __name__ == "__main__":
    main()
