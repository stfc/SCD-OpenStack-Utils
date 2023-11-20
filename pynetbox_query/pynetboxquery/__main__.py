import sys
from pynetboxquery.utils.parsers import Parsers
from pynetboxquery.user_methods.upload_devices_to_netbox import upload_devices_to_netbox
from pynetboxquery.user_methods.validate_data_fields_in_netbox import (
    validate_data_fields_in_netbox,
)


def main():
    argparse_args = Parsers().arg_parser()
    kwargs = vars(argparse_args)
    match kwargs["subparsers"]:
        case action if action in ["create_device", "create"]:
            upload_devices_to_netbox(**kwargs)
        case action if action in ["validate_objects_in_netbox", "validate"]:
            validate_data_fields_in_netbox(**kwargs)
        case _:
            sys.stdout.write(
                f"""Invalid action "{kwargs["subparsers"]}". See pynetboxquery --help for actions.\n"""
            )
    sys.stdout.write("Done.")


if __name__ == "__main__":
    main()
