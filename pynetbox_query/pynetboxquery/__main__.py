from pynetboxquery.utils.parsers import Parsers
from pynetboxquery.user_methods.upload_devices_to_netbox import upload_devices_to_netbox
from pynetboxquery.user_methods.validate_data_fields_in_netbox import (
    validate_data_fields_in_netbox,
)


def main():
    """
    This function will:
    Run the argparse method to collect arguments from the CLI.
    Then run the correct user script for the action specified in the CLI.
    """
    argparse_args = Parsers().arg_parser()
    kwargs = vars(argparse_args)
    match kwargs["subparsers"]:
        case action if action in ["create_device", "create"]:
            upload_devices_to_netbox(**kwargs)
        case action if action in ["validate_objects_in_netbox", "validate"]:
            validate_data_fields_in_netbox(**kwargs)
        case _:
            print(
                f"""Invalid action "{kwargs["subparsers"]}". See pynetboxquery --help for actions.\n"""
            )
    print("Done.")


if __name__ == "__main__":
    main()
