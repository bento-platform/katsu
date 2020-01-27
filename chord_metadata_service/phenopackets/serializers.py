from rest_framework import serializers
from .models import *
from jsonschema import Draft7Validator, FormatChecker
from chord_metadata_service.restapi.schemas import *
from chord_metadata_service.restapi.validators import JsonSchemaValidator
from chord_metadata_service.restapi.serializers import GenericSerializer
from chord_metadata_service.restapi.fhir_utils import *
import re


#############################################################
#                                                           #
#                  Metadata  Serializers                    #
#                                                           #
#############################################################

class ResourceSerializer(GenericSerializer):
    class Meta:
        model = Resource
        fields = '__all__'


class MetaDataSerializer(GenericSerializer):
    resources = ResourceSerializer(read_only=True, many=True)

    class Meta:
        model = MetaData
        fields = '__all__'

    def validate_updates(self, value):
        """
        Check updates against schema.
        Timestamp must follow ISO8601 UTC standard
        e.g. 2018-06-10T10:59:06Z

        """

        if isinstance(value, list):
            for item in value:
                validation = Draft7Validator(
                    UPDATE_SCHEMA, format_checker=FormatChecker(formats=['date-time'])
                    ).is_valid(item)
                if not validation:
                    raise serializers.ValidationError("Update is not valid")
        return value

    def validate_external_references(self, value):
        if isinstance(value, list):
            for item in value:
                validation = Draft7Validator(EXTERNAL_REFERENCE).is_valid(item)
                if not validation:
                    raise serializers.ValidationError("Not valid JSON schema for this field.")
        return value


#############################################################
#                                                           #
#              Phenotypic Data  Serializers                 #
#                                                           #
#############################################################

class PhenotypicFeatureSerializer(GenericSerializer):
    type = serializers.JSONField(source='pftype',
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)])
    severity = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    onset = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    evidence = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=EVIDENCE)],
        allow_null=True, required=False)

    class Meta:
        model = PhenotypicFeature
        exclude = ['pftype']
        # meta info for converting to FHIR
        fhir_datatype_plural = 'observations'
        class_converter = fhir_observation

    def validate_modifier(self, value):
        if isinstance(value, list):
            for item in value:
                validation = Draft7Validator(ONTOLOGY_CLASS).is_valid(item)
                if not validation:
                    raise serializers.ValidationError("Not valid JSON schema for this field.")
        return value


class ProcedureSerializer(GenericSerializer):
    code = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)])
    body_site = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)

    class Meta:
        model = Procedure
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'specimen.collections'
        class_converter = fhir_specimen_collection

    def create(self, validated_data):
        if validated_data.get('body_site'):
            instance, _ = Procedure.objects.get_or_create(**validated_data)
        else:
            instance, _ = Procedure.objects.get_or_create(
                code=validated_data.get('code'), body_site__isnull=True)
        return instance


class HtsFileSerializer(GenericSerializer):

    class Meta:
        model = HtsFile
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'document_references'
        class_converter = fhir_document_reference


class GeneSerializer(GenericSerializer):
    alternate_ids = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        allow_empty=True, required=False)

    class Meta:
        model = Gene
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'observations'
        class_converter = fhir_obs_component_region_studied


class VariantSerializer(GenericSerializer):
    allele = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ALLELE_SCHEMA)])
    zygosity = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)

    class Meta:
        model = Variant
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'observations'
        class_converter = fhir_obs_component_variant

    def to_representation(self, obj):
        """ Change 'allele_type' field name to allele type value. """

        output = super().to_representation(obj)
        output[obj.allele_type] = output.pop('allele')
        return output

    def to_internal_value(self, data):
        """ When writing back to db change field name back to 'allele'. """

        if 'allele' not in data.keys():
            allele_type = data.get('allele_type') # e.g. spdiAllele
            # split by uppercase
            normilize = filter(None, re.split("([A-Z][^A-Z]*)", allele_type))
            normilized_allele_type = '_'.join([i.lower() for i in normilize])
            data['allele'] = data.pop(normilized_allele_type)
        return super(VariantSerializer, self).to_internal_value(data=data)


class DiseaseSerializer(GenericSerializer):
    term = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)])
    onset = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=DISEASE_ONSET)])

    class Meta:
        model = Disease
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'conditions'
        class_converter = fhir_condition

    def validate_disease_stage(self, value):
        if isinstance(value, list):
            for item in value:
                validation = Draft7Validator(ONTOLOGY_CLASS).is_valid(item)
                if not validation:
                    raise serializers.ValidationError(
                        "Not valid JSON schema for this field."
                        )
        return value


class BiosampleSerializer(GenericSerializer):
    sampled_tissue = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)])
    taxonomy = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    individual_age_at_collection = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=AGE_OR_AGE_RANGE)],
        allow_null=True, required=False)
    histological_diagnosis = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    tumor_progression = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    tumor_grade = serializers.JSONField(
        validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
        allow_null=True, required=False)
    phenotypic_features = PhenotypicFeatureSerializer(read_only=True,
        many=True, exclude_when_nested=['id', 'biosample'])
    procedure = ProcedureSerializer(exclude_when_nested=['id'])

    class Meta:
        model = Biosample
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'specimens'
        class_converter = fhir_specimen

    def validate_diagnostic_markers(self, value):
        if isinstance(value, list):
            for item in value:
                validation = Draft7Validator(ONTOLOGY_CLASS).is_valid(item)
                if not validation:
                    raise serializers.ValidationError(
                        "Not valid JSON schema for this field."
                        )
        return value

    def create(self, validated_data):
        procedure_data = validated_data.pop('procedure')
        procedure_model, _ = Procedure.objects.get_or_create(**procedure_data)
        biosample = Biosample.objects.create(procedure=procedure_model, **validated_data)
        return biosample


class SimplePhenopacketSerializer(GenericSerializer):
    phenotypic_features = PhenotypicFeatureSerializer(
        read_only=True, many=True, exclude_when_nested=['id', 'biosample'])

    class Meta:
        model = Phenopacket
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'compositions'
        class_converter = fhir_composition

    def to_representation(self, instance):
        """"
        Overriding this method to allow post Primary Key for FK and M2M
        objects and return their nested serialization.

        """
        response = super().to_representation(instance)
        response['biosamples'] = BiosampleSerializer(
            instance.biosamples, many=True, required=False,
            exclude_when_nested=["individual"]
            ).data
        response['genes'] = GeneSerializer(
            instance.genes, many=True, required=False
            ).data
        response['variants'] = VariantSerializer(
            instance.variants, many=True, required=False
            ).data
        response['diseases'] = DiseaseSerializer(
            instance.diseases, many=True, required=False
            ).data
        response['hts_files'] = HtsFileSerializer(
            instance.hts_files, many=True, required=False
            ).data
        response['meta_data'] = MetaDataSerializer(
            instance.meta_data, exclude_when_nested=['id']
            ).data
        return response


class PhenopacketSerializer(SimplePhenopacketSerializer):

    def to_representation(self, instance):
        # Phenopacket serializer for nested individuals - need to import here to
        # prevent circular import issues.
        from chord_metadata_service.patients.serializers import IndividualSerializer
        response = super().to_representation(instance)
        response['subject'] = IndividualSerializer(
            instance.subject,
            exclude_when_nested=["phenopackets", "biosamples"]
            ).data
        return response


#############################################################
#                                                           #
#                Interpretation Serializers                 #
#                                                           #
#############################################################

class GenomicInterpretationSerializer(GenericSerializer):

    class Meta:
        model = GenomicInterpretation
        fields = '__all__'


class DiagnosisSerializer(GenericSerializer):

    class Meta:
        model = Diagnosis
        fields = '__all__'


class InterpretationSerializer(GenericSerializer):

    class Meta:
        model = Interpretation
        fields = '__all__'
