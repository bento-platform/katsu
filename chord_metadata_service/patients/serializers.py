from rest_framework import serializers
from .models import *
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS
from chord_metadata_service.restapi.validators import JsonSchemaValidator
from chord_metadata_service.phenopackets.serializers import (
	BiosampleSerializer, PhenopacketSerializer)
from chord_metadata_service.restapi.serializers import GenericSerializer


class IndividualSerializer(GenericSerializer):
	taxonomy = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True, required=False
		)
	biosamples = BiosampleSerializer(read_only=True, many=True,
		exclude_when_nested=['individual'])
	phenopackets = PhenopacketSerializer(read_only=True, many=True)

	class Meta:
		model = Individual
		fields = '__all__'
