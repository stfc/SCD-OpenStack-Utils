# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
# Disabling this Pylint error as these classes do not need Docstring.
# They are just errors
# pylint: disable = C0115
"""Custom exceptions for the package."""


class DeviceFoundError(Exception):
    pass


class DeviceTypeNotFoundError(Exception):
    pass


class FileTypeNotSupportedError(Exception):
    pass


class DelimiterNotSpecifiedError(Exception):
    pass


class SheetNameNotSpecifiedError(Exception):
    pass


class ApiObjectNotParsedError(Exception):
    pass


class UserMethodNotFoundError(Exception):
    pass
