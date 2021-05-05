#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    "marshmallow>=3.11.1",
    "marshmallow-jsonschema>=0.11.1",
    "jsonschema>=3.2.0"
]

extras_require = {
    "dev": ["pytest>=3.6", "flake8"]
}


setup(
    name="nwss",
    version="0.0.1",
    author="DataMade",
    author_email="info@datamade.us",
    license="MIT",
    description="A marshmallow schema for the \
                National Wastewater Surveillance System",
    long_description="",
    url="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
    platforms=["any"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
