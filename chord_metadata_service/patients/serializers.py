from rest_framework import serializers
from .models import *
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS
from chord_metadata_service.restapi.validators import JsonSchemaValidator


class IndividualSerializer(serializers.ModelSerializer):
	taxonomy = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True
		)

	class Meta:
		model = Individual
		fields = '__all__'
