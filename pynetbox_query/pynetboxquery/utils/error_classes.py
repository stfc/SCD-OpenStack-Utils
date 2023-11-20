# Disabling this Pylint error as these classes do not need Docstring.
# They are just errors
# pylint: disable = C0115
"""Custom exceptions for the package."""


class DeviceFoundError(Exception):
    pass


class DeviceTypeNotFoundError(Exception):
    pass


class FileTypeNotSupported(Exception):
    pass


class DelimiterNotSpecifiedError(Exception):
    pass


class SheetNameNotSpecifiedError(Exception):
    pass


class ApiObjectNotParsedError(Exception):
    pass
