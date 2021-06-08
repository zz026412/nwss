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
    version="1.0.0",
    author="DataMade",
    author_email="info@datamade.us",
    license="MIT",
    description="A marshmallow schema for the \
                National Wastewater Surveillance System",
    url="https://github.com/datamade/nwss-data-standard",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
    platforms=["any"],
    keywords=[
        "National Wastewater Surveillance System",
        "NWSS",
        "DCIPHER",
        "United States Center for Disease Control",
        "COVID-19",
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
