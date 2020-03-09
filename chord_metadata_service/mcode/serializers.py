from rest_framework import serializers
from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import *
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS, QUANTITY
from chord_metadata_service.restapi.validators import JsonSchemaValidator


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
    class Meta:
        model = CancerCondition
        fields = '__all__'


class TNMStagingSerializer(GenericSerializer):
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