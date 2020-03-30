from rest_framework import serializers
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS, AGE_OR_AGE_RANGE
from chord_metadata_service.restapi.validators import JsonSchemaValidator, ontologyListValidator, keyValueValidator
from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import Experiment


class ExperimentSerializer(GenericSerializer):
    class Meta:
        model = Experiment
        fields = '__all__'
