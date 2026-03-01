import sys
import os
import pathlib
from setuptools import setup

version = "0.1.0"
package_name = "xspectrampoline"
readme = pathlib.Path("README.md").read_text()

setup(
    author="Fergus Baker",
    author_email="fergus@cosroe.com",
    description="A package for distributing the HEASOFT / XSPEC model library.",
    keywords=["xspec", "heasoft"],
    long_description=readme,
    python_requires=">=3.6",
    install_requires=["numpy>=1.24"],
    license="GPL-3.0-or-later",
    name=package_name,
    version=version,
    packages=[package_name],
    url=f"https://github.com/fjebaker/{package_name}",
    classifiers=[
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
    ],
)
