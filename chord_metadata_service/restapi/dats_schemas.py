import json
import os
from glob import glob


def get_dats_schema(field):
	"""
	Call this function when validating a field.
	Returns json schema for the specified field.
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

	for filename in glob(os.path.join('chord_metadata_service/dats/', '*.json')):
		# parse e.g. dats\access_schema.json to get just name
		schema_name = filename.split('\\')[1].split('.')[0]
		field_schema_name = fields_mapping.get(field, None)
		if schema_name == field_schema_name:
			schema_file = open(filename)
			schema = json.loads(schema_file.read())
			return schema


def _get_creators_schema(creator_type):
	""" Internal function to get creators schemas. """

	dats_creators_schema = open('chord_metadata_service/dats/{}.json'.format(creator_type))
	creator_schema = json.loads(dats_creators_schema.read())
	return creator_schema


CREATORS = { 
   "$schema":"http://json-schema.org/draft-04/schema",
   "title":"Creators schema",
   "description":"Creators of the dataset.",
   "type":"array",
   "items": {
	    "oneOf": [
	        _get_creators_schema('person_schema'),
	        _get_creators_schema('organization_schema')
	    ]
	}
}
