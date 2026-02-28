import sys
import os
from setuptools import setup

version = "0.1.0"
package_name = "xspectrampoline"

setup(
    author="Fergus Baker",
    author_email="fergus@cosroe.com",
    description="A package for distributing the XSPEC model library.",
    python_requires=">=3.6",
    install_requires=["numpy>=1.24"],
    license="GPL-3.0-or-later",
    name=package_name,
    version=version,
    packages=[package_name],
)
