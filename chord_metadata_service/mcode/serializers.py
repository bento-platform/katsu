from rest_framework import serializers
from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import *
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS, QUANTITY, COMPLEX_ONTOLOGY
from chord_metadata_service.restapi.validators import JsonSchemaValidator
from jsonschema import Draft7Validator


class GeneticVariantTestedSerializer(GenericSerializer):
    method = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    variant_tested_identifier = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    data_value = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)

    class Meta:
        model = GeneticVariantTested
        fields = '__all__'


class GeneticVariantFoundSerializer(GenericSerializer):
    method = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    variant_found_identifier = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    genomic_source_class = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    
    class Meta:
        model = GeneticVariantFound
        fields = '__all__'


class GenomicsReportSerializer(GenericSerializer):
    test_name = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    specimen_type = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)

    class Meta:
        model = GenomicsReport
        fields = '__all__'


class LabsVitalSerializer(GenericSerializer):
    body_height = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=QUANTITY)],
        allow_null=True, required=False)
    body_weight = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=QUANTITY)],
        allow_null=True, required=False)
    blood_pressure_diastolic = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=QUANTITY)],
        allow_null=True, required=False)
    blood_pressure_systolic = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=QUANTITY)],
        allow_null=True, required=False)

    class Meta:
        model = LabsVital
        fields = '__all__'


class CancerConditionSerializer(GenericSerializer):
    clinical_status = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    condition_code = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    histology_morphology_behavior = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)

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
    stage_group = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=COMPLEX_ONTOLOGY)],
        allow_null=True, required=False)

    class Meta:
        model = TNMStaging
        fields = '__all__'


class CancerRelatedProcedureSerializer(GenericSerializer):
    class Meta:
        model = CancerRelatedProcedure
        fields = '__all__'


class MedicationStatementSerializer(GenericSerializer):
    class Meta:
        model = MedicationStatement
        fields = '__all__'