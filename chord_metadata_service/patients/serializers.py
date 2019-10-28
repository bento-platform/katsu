from chord_lib.schemas.chord import CHORD_DATA_USE_SCHEMA
from rest_framework import serializers, validators
from .models import *
from jsonschema import validate, ValidationError, Draft7Validator, FormatChecker
from .schemas import ALLELE_SCHEMA, UPDATE_SCHEMA


##### Allele classes have to be serialized in VarianSerializer #####
# TODO move
ONTOLOGY_CLASS = {
"$schema": "http://json-schema.org/draft-07/schema#",
	"$id": "todo",
	"title": "Ontology class schema",
	"description": "todo",
	"type": "object",
	"properties": {
		"id": {"type": "string", "description": "CURIE style identifier"},
		"label": {"type": "string", "description": "Human-readable class name"}
	},
	"required": ["id", "label"]

}


class IndividualSerializer(serializers.ModelSerializer):

	class Meta:
		model = Individual
		fields = '__all__'
