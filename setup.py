#!/usr/bin/env python

import configparser
import os
import setuptools

with open("README.md", "r") as rf:
    long_description = rf.read()

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "chord_metadata_service", "package.cfg"))

setuptools.setup(
    name=config["package"]["name"],
    version=config["package"]["version"],

    python_requires=">=3.6",
    install_requires=[
        "chord_lib[django]==0.7.0",
        "Django>=2.2,<3.0",
        "django-filter>=2.2,<3.0",
        "django-nose>=1.4,<2.0",
        "djangorestframework>=3.11,<3.12",
        "djangorestframework-camel-case>=1.1,<2.0",
        "django-rest-swagger==2.2.0",
        "elasticsearch==7.1.0",
        "fhirclient>=3.2,<4.0",
        "jsonschema>=3.2,<4.0",
        "psycopg2-binary>=2.8,<3.0",
        "python-dateutil>=2.8,<3.0",
        "PyYAML>=5.3,<6.0",
        "strict-rfc3339==0.7",
        "rdflib==4.2.2",
        "rdflib-jsonld==0.4.0",
        "requests>=2.23,<3.0",
        "rfc3987==1.3.8",
        "uritemplate>=3.0,<4.0",
    ],

    author=config["package"]["authors"],

    description="An implementation of a variant store for the CHORD project.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=setuptools.find_packages(),
    include_package_data=True,

    url="https://github.com/c3g/chord_metadata_service",
    license="LGPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent"
    ]
)
