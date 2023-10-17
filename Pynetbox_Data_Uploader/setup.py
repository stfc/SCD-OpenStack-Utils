from setuptools import setup, find_packages

VERSION = "0.1.0"
DESCRIPTION = "python package for PYNETBOX tools"

LONG_DESCRIPTION = """Python package to interact with Netbox from cli."""

setup(
    name="Pynetbox_Data_Uploader",
    version=VERSION,
    author="Kalibh Halford",
    author_email="<kalibh.halford@stfc.ac.uk>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    package_dir={"Pynetbox_Data_Uploader": "lib"},
    python_requires=">=3.9",
    install_requires=[],
    keywords=["python"],
)
