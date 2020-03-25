from rest_framework import serializers
from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import *
from chord_metadata_service.restapi.schemas import (
    ONTOLOGY_CLASS, QUANTITY, COMPLEX_ONTOLOGY, TIME_OR_PERIOD, TUMOR_MARKER_TEST
)
from chord_metadata_service.restapi.validators import JsonSchemaValidator
from jsonschema import Draft7Validator


class GeneticVariantTestedSerializer(GenericSerializer):

    class Meta:
        model = GeneticVariantTested
        fields = '__all__'


class GeneticVariantFoundSerializer(GenericSerializer):
    
    class Meta:
        model = GeneticVariantFound
        fields = '__all__'


class GenomicsReportSerializer(GenericSerializer):

    class Meta:
        model = GenomicsReport
        fields = '__all__'


class LabsVitalSerializer(GenericSerializer):

    class Meta:
        model = LabsVital
        fields = '__all__'


class CancerConditionSerializer(GenericSerializer):

    class Meta:
        model = CancerCondition
        fields = '__all__'

    def validate_body_location_code(self, value):
        if isinstance(value, list):
            for item in value:
                validation = Draft7Validator(ONTOLOGY_CLASS).is_valid(item)
                if not validation:
                    raise serializers.ValidationError("Not valid JSON schema for this field.")
        return value


class TNMStagingSerializer(GenericSerializer):
    #TODO URI syntax examples for tests https://tools.ietf.org/html/rfc3986

    class Meta:
        model = TNMStaging
        fields = '__all__'


class CancerRelatedProcedureSerializer(GenericSerializer):
    code = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    occurence_time_or_period = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=TIME_OR_PERIOD, format_checker=['date-time'])],
        allow_null=True, required=False)
    treatment_intent = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)

    class Meta:
        model = CancerRelatedProcedure
        fields = '__all__'

    def validate_target_body_site(self, value):
        if isinstance(value, list):
            for item in value:
                validation = Draft7Validator(ONTOLOGY_CLASS).is_valid(item)
                if not validation:
                    raise serializers.ValidationError("Not valid JSON schema for this field.")
        return value


class MedicationStatementSerializer(GenericSerializer):
    medication_code = serializers.JSONField(validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)])
    treatment_intent = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)

    def validate_termination_reason(self, value):
        if isinstance(value, list):
            for item in value:
                validation = Draft7Validator(ONTOLOGY_CLASS).is_valid(item)
                if not validation:
                    raise serializers.ValidationError("Not valid JSON schema for this field.")
        return value


    class Meta:
        model = MedicationStatement
        fields = '__all__'


class MCodePacketSerializer(GenericSerializer):

    class Meta:
        model = MCodePacket
        fields = '__all__'
