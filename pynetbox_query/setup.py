# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
from setuptools import setup, find_packages

VERSION = "0.1.0"
DESCRIPTION = "python package for pynetbox tools"

LONG_DESCRIPTION = """Python package to query Netbox."""

setup(
    name="pynetboxQuery",
    version=VERSION,
    author="Kalibh Halford",
    author_email="<kalibh.halford@stfc.ac.uk>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    python_requires=">=3.10",
    keywords=["python"],
)
