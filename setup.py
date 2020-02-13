#!/usr/bin/env python

import setuptools

with open("README.md", "r") as rf:
    long_description = rf.read()

setuptools.setup(
    name="chord_metadata_service",
    version="0.2.0",

    python_requires=">=3.6",
    install_requires=[
        "chord_lib[django]==0.2.0",
        "Django>=2.2,<3.0",
        "django-filter>=2.2,<3.0",
        "django-nose>=1.4,<2.0",
        "djangorestframework>=3.10,<3.11",
        "djangorestframework-camel-case",
        "elasticsearch==7.1.0",
        "fhirclient>=3.2,<4.0",
        "jsonschema>=3.2,<4.0",
        "psycopg2-binary>=2.8,<3.0",
        "python-dateutil>=2.8,<3.0",
        "PyYAML>=5.3,<6.0",
        "rdflib==4.2.2",
        "rdflib-jsonld==0.4.0",
        "requests>=2.22,<3.0",
        "uritemplate>=3.0,<4.0",
    ],

    author="Ksenia Zaytseva, David Lougheed",

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
