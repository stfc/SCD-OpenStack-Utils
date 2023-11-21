import sys
from pynetboxquery.user_methods.upload_devices_to_netbox import main_upload_devices_to_netbox
from pynetboxquery.user_methods.validate_data_fields_in_netbox import main_validate_data_fields_in_netbox


def main():
    """
    This function will run the correct user method for the action specified in the CLI.
    """
    action = sys.argv[1]
    match action:
        case alias if alias in ["create_device", "create"]:
            main_upload_devices_to_netbox()
        case alias if alias in ["validate_objects_in_netbox", "validate"]:
            main_validate_data_fields_in_netbox()
        case _:
            print(
                f"""Invalid action "{action}". See pynetboxquery --help for actions.\n"""
            )
    print("Done.")


if __name__ == "__main__":
    main()
