import json
import os

from functools import cache
from jsonschema import Draft4Validator
from glob import glob
from pathlib import Path

__all__ = [
    "get_dats_schema",
    "get_dats_schema_validator",
    "CREATORS",
]

DATS_PATH = os.path.join(Path(os.path.dirname(os.path.realpath(__file__))).parent, "dats")


@cache  # If no exception is raised, cache to result to avoid repetitive file reading
def get_dats_schema(field: str):
    """
    Call this function when validating a field.
    Returns json schema for the specified field.
    Uses functools.cache to avoid slow disk IO for reading the file every time.
    """

    # mapping dataset model fields to dats schemas
    fields_mapping = {
        'alternate_identifiers': 'alternate_identifier_info_schema',
        'related_identifiers': 'related_identifier_info_schema',
        'dates': 'date_info_schema',
        'stored_in': 'data_repository_schema',
        'spatial_coverage': 'place_schema',
        'types': 'data_type_schema',
        'distributions': 'dataset_distribution_schema',
        'dimensions': 'dimension_schema',
        'primary_publications': 'publication_schema',
        'citations': 'publication_schema',
        'produced_by': 'study_schema',
        'licenses': 'license_schema',
        'acknowledges': 'grant_schema',
        'keywords': 'annotation_schema'
    }

    for filename in glob(os.path.join(DATS_PATH, '*.json')):
        schema_name = Path(filename).stem
        field_schema_name = fields_mapping.get(field, None)
        if schema_name == field_schema_name:
            with open(filename) as schema_file:
                schema = json.loads(schema_file.read())
            return schema

    # Avoid caching None responses; also we should know if this occurs...
    raise Exception(f"DATS schema not found: {field}")


@cache
def get_dats_schema_validator(field: str) -> Draft4Validator:
    """
    Cache DATS field schema validators to avoid initializing them on the fly as much.
    """
    return Draft4Validator(get_dats_schema(field))


def _get_creators_schema(creator_type):
    """ Internal function to get creators schemas. """

    dats_creators_schema = open(os.path.join(DATS_PATH, '{}.json'.format(creator_type)))
    creator_schema = json.loads(dats_creators_schema.read())
    dats_creators_schema.close()
    return creator_schema


CREATORS = {
    "$schema": "http://json-schema.org/draft-04/schema",
    "title": "Creators schema",
    "description": "Creators of the dataset.",
    "type": "array",
    "items": {
        "anyOf": [
            _get_creators_schema('person_schema'),
            _get_creators_schema('organization_schema')
        ]
    }
}
