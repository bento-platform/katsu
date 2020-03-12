from rest_framework import serializers
from chord_metadata_service.phenopackets.serializers import (
    BiosampleSerializer,
    SimplePhenopacketSerializer
)
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS, AGE_OR_AGE_RANGE, COMORBID_CONDITION
from chord_metadata_service.restapi.validators import JsonSchemaValidator
from chord_metadata_service.restapi.serializers import GenericSerializer
from chord_metadata_service.restapi.fhir_utils import fhir_patient
from .models import Individual


class IndividualSerializer(GenericSerializer):
    taxonomy = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True,
        required=False
    )
    age = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=AGE_OR_AGE_RANGE)],
        allow_null=True,
        required=False
    )
    comorbid_condition = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=COMORBID_CONDITION)],
        allow_null=True,
        required=False
    )
    biosamples = BiosampleSerializer(
        read_only=True, many=True, exclude_when_nested=['individual'])

    phenopackets = SimplePhenopacketSerializer(
        read_only=True, many=True, exclude_when_nested=['subject'])

    class Meta:
        model = Individual
        fields = "__all__"
        # meta info for converting to FHIR
        fhir_datatype_plural = 'patients'
        class_converter = fhir_patient
