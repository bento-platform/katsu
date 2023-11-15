from rest_framework import serializers
from .models import (
    MetaData,
    PhenotypicFeature,
    HtsFile,
    Gene,
    Disease,
    Biosample,
    Phenopacket,
    GenomicInterpretation,
    Diagnosis,
    Interpretation,
    VariantInterpretation,
    VariationDescriptor,
    GeneDescriptor,
)
from chord_metadata_service.resources.serializers import ResourceSerializer
from chord_metadata_service.experiments.serializers import ExperimentSerializer
from chord_metadata_service.restapi import fhir_utils
from chord_metadata_service.restapi.serializers import GenericSerializer


__all__ = [
    "MetaDataSerializer",
    "PhenotypicFeatureSerializer",
    "HtsFileSerializer",
    "GeneSerializer",
    "DiseaseSerializer",
    "BiosampleSerializer",
    "SimplePhenopacketSerializer",
    "PhenopacketSerializer",
    "VariantDescriptorSerializer",
    "VariantInterpretationSerializer",
    "GenomicInterpretationSerializer",
    "GeneDescriptorSerializer",
    "DiagnosisSerializer",
    "InterpretationSerializer",
]


#############################################################
#                                                           #
#                  Metadata  Serializers                    #
#                                                           #
#############################################################


class MetaDataSerializer(GenericSerializer):
    resources = ResourceSerializer(read_only=True, many=True)

    class Meta:
        model = MetaData
        fields = '__all__'


#############################################################
#                                                           #
#              Phenotypic Data  Serializers                 #
#                                                           #
#############################################################

class PhenotypicFeatureSerializer(GenericSerializer):
    always_include = (
        "excluded",
    )

    type = serializers.JSONField(source='pftype')

    class Meta:
        model = PhenotypicFeature
        exclude = ['pftype']
        # meta info for converting to FHIR
        fhir_datatype_plural = 'observations'
        class_converter = fhir_utils.fhir_observation


class HtsFileSerializer(GenericSerializer):

    class Meta:
        model = HtsFile
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'document_references'
        class_converter = fhir_utils.fhir_document_reference


class GeneSerializer(GenericSerializer):
    alternate_ids = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        allow_empty=True, required=False)

    class Meta:
        model = Gene
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'observations'
        class_converter = fhir_utils.fhir_obs_component_region_studied


class DiseaseSerializer(GenericSerializer):

    class Meta:
        model = Disease
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'conditions'
        class_converter = fhir_utils.fhir_condition


class BiosampleSerializer(GenericSerializer):
    phenotypic_features = PhenotypicFeatureSerializer(
        read_only=True, many=True, exclude_when_nested=['id', 'biosample'])
    experiments = ExperimentSerializer(read_only=True, many=True, source='experiment_set')

    class Meta:
        model = Biosample
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'specimens'
        class_converter = fhir_utils.fhir_specimen

    def create(self, validated_data):
        biosample = Biosample.objects.create(**validated_data)
        return biosample

    def update(self, instance, validated_data):
        instance.sampled_tissue = validated_data.get('sampled_tissue', instance.sampled_tissue)
        instance.time_of_collection = validated_data.get('time_of_collection', instance.time_of_collection)
        instance.taxonomy = validated_data.get('taxonomy', instance.taxonomy)
        instance.histological_diagnosis = validated_data.get('histological_diagnosis', instance.histological_diagnosis)
        instance.tumor_progression = validated_data.get('tumor_progression', instance.tumor_progression)
        instance.tumor_grade = validated_data.get('tumor_grade', instance.tumor_grade)
        instance.diagnostic_markers = validated_data.get('diagnostic_markers', instance.diagnostic_markers)
        instance.procedure = validated_data.get('procedure', instance.procedure)
        instance.save()
        return instance


#############################################################
#                                                           #
#                Interpretation Serializers                 #
#                                                           #
#############################################################
class GeneDescriptorSerializer(GenericSerializer):

    class Meta:
        model = GeneDescriptor
        fields = '__all__'


class VariantDescriptorSerializer(GenericSerializer):
    gene_context = GeneDescriptorSerializer(many=False, required=False)

    class Meta:
        model = VariationDescriptor
        fields = '__all__'


class VariantInterpretationSerializer(GenericSerializer):

    class Meta:
        model = VariantInterpretation
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["variation_descriptor"] = VariantDescriptorSerializer(
            instance.variation_descriptor, many=False, required=True).data
        return response


class GenomicInterpretationSerializer(GenericSerializer):

    class Meta:
        model = GenomicInterpretation
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)

        # May contain a gene_descriptor or a variant_interpretation, not both
        if instance.gene_descriptor:
            response["gene_descriptor"] = GeneDescriptorSerializer(
                instance.gene_descriptor, many=False, required=False).data
        elif instance.variant_interpretation:
            response["variant_interpretation"] = VariantInterpretationSerializer(
                instance.variant_interpretation, many=False, required=False).data

        return response


class DiagnosisSerializer(GenericSerializer):

    genomic_interpretations = GenomicInterpretationSerializer(many=True, required=False)

    class Meta:
        model = Diagnosis
        fields = '__all__'


class InterpretationSerializer(GenericSerializer):

    class Meta:
        model = Interpretation
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["diagnosis"] = DiagnosisSerializer(instance.diagnosis, many=False, required=False).data
        return response


#############################################################
#                                                           #
#              Phenopacket Data  Serializers                 #
#                                                           #
#############################################################


class SimplePhenopacketSerializer(GenericSerializer):
    phenotypic_features = PhenotypicFeatureSerializer(
        read_only=True, many=True, exclude_when_nested=['id', 'biosample'])
    interpretations = InterpretationSerializer(many=True, required=False)
    diseases = DiseaseSerializer(many=True, required=False)

    class Meta:
        model = Phenopacket
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'compositions'
        class_converter = fhir_utils.fhir_composition

    def to_representation(self, instance):
        """"
        Overriding this method to allow post Primary Key for FK and M2M
        objects and return their nested serialization.

        """
        response = super().to_representation(instance)
        response['biosamples'] = BiosampleSerializer(instance.biosamples, many=True, required=False,
                                                     exclude_when_nested=["individual"]).data
        response['meta_data'] = MetaDataSerializer(instance.meta_data, exclude_when_nested=['id']).data
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
