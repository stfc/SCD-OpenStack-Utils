from setuptools import setup, find_packages

VERSION = "0.0.2"
DESCRIPTION = "python package for IRISCAST tools"

LONG_DESCRIPTION = """Python package to get power and CPU/RAM usage statistics"""

setup(
    name="iriscasttools",
    version=VERSION,
    author="Anish Mudaraddi",
    author_email="<anish.mudaraddi@stfc.ac.uk>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[],
    keywords=["python"],
)
