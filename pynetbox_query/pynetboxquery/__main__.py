# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
from importlib import import_module
import sys
from pynetboxquery.utils.error_classes import UserMethodNotFoundError


def main():
    """
    This function will run the correct user method for the action specified in the CLI.
    """
    user_methods_names = ["upload_devices_to_netbox", "validate_data_fields_in_netbox"]
    for user_method in user_methods_names:
        user_method_module = import_module(f"pynetboxquery.user_methods.{user_method}")
        user_method_class = getattr(user_method_module, "Main")()
        aliases = user_method_class.aliases()
        if sys.argv[1] in aliases:
            user_method_module.Main().main()
            return
    raise UserMethodNotFoundError(f"The user method {sys.argv[1]} was not found.")


if __name__ == "__main__":
    main()
