from rest_framework import serializers

from chord_metadata_service.restapi.utils import computed_property
from .models import (
    MetaData,
    PhenotypicFeature,
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
from chord_metadata_service.experiments.serializers import ExperimentSerializer
from chord_metadata_service.geo.ingest import get_or_create_geo_location
from chord_metadata_service.geo.serializers import GeoLocationSerializer
from chord_metadata_service.resources.serializers import ResourceSerializer
from chord_metadata_service.restapi.serializers import GenericSerializer


__all__ = [
    "MetaDataSerializer",
    "PhenotypicFeatureSerializer",
    "DiseaseSerializer",
    "SimpleBiosampleSerializer",
    "BiosampleSerializer",
    "SimplePhenopacketSerializer",
    "PhenopacketSerializer",
    "VariationDescriptorSerializer",
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
    # Note: this serializer is always nested

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
    # Note: this serializer is always nested

    always_include = (
        "excluded",
    )

    type = serializers.JSONField(source='pftype')

    class Meta:
        model = PhenotypicFeature
        exclude = ('id', 'biosample', 'phenopacket', 'pftype')


class DiseaseSerializer(GenericSerializer):
    # Note: this serializer is always nested

    always_include = (
        "excluded",
    )

    class Meta:
        model = Disease
        fields = '__all__'


class SimpleBiosampleSerializer(GenericSerializer):
    # Note: this serializer is always nested

    phenotypic_features = PhenotypicFeatureSerializer(read_only=True, many=True)
    location_collected = GeoLocationSerializer(required=False)

    class Meta:
        model = Biosample
        exclude = ("individual",)


class BiosampleSerializer(GenericSerializer):
    phenotypic_features = PhenotypicFeatureSerializer(read_only=True, many=True)
    experiments = ExperimentSerializer(read_only=True, many=True, source='experiment_set')
    location_collected = GeoLocationSerializer(required=False)

    class Meta:
        model = Biosample
        fields = '__all__'

    def create(self, validated_data):
        if (
            "location_collected" in validated_data
            and isinstance(location_collected := validated_data["location_collected"], dict)
        ):
            validated_data["location_collected"] = get_or_create_geo_location(location_collected)
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

        if location_collected := validated_data.get("location_collected"):
            instance.location_collected = get_or_create_geo_location(location_collected)

        instance.save()
        return instance


#############################################################
#                                                           #
#                Interpretation Serializers                 #
#                                                           #
#############################################################
class GeneDescriptorSerializer(GenericSerializer):
    # Note: this serializer is always nested

    class Meta:
        model = GeneDescriptor
        fields = '__all__'


class VariationDescriptorSerializer(GenericSerializer):
    # Note: this serializer is always nested

    gene_context = GeneDescriptorSerializer(many=False, required=False)

    class Meta:
        model = VariationDescriptor
        fields = '__all__'


class VariantInterpretationSerializer(GenericSerializer):
    # Note: this serializer is always nested

    class Meta:
        model = VariantInterpretation
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["variation_descriptor"] = VariationDescriptorSerializer(
            instance.variation_descriptor, many=False, required=True).data
        return response


class GenomicInterpretationSerializer(GenericSerializer):
    # Note: this serializer is always nested

    class Meta:
        model = GenomicInterpretation
        exclude = ["subject", "biosample"]

    def to_representation(self, instance):
        response = super().to_representation(instance)

        # May contain a gene_descriptor or a variant_interpretation, not both
        if instance.gene_descriptor:
            response["gene_descriptor"] = GeneDescriptorSerializer(
                instance.gene_descriptor, many=False, required=False).data
        elif instance.variant_interpretation:
            response["variant_interpretation"] = VariantInterpretationSerializer(
                instance.variant_interpretation, many=False, required=False).data

        # The 'subject_or_biosample_id' value is obtained from the referenced subject/biosample
        # The '__related_type' property is added to extra_properties as a computed value ("__" prefix)
        # This allows us to disambiguate on the client side for links
        extra_properties = response.get("extra_properties", {})
        computed_related_type = computed_property("related_type")
        if instance.subject:
            response["subject_or_biosample_id"] = instance.subject.id
            extra_properties[computed_related_type] = "subject"
        elif instance.biosample:
            response["subject_or_biosample_id"] = instance.biosample.id
            extra_properties[computed_related_type] = "biosample"

        response["extra_properties"] = extra_properties
        return response


class DiagnosisSerializer(GenericSerializer):
    # Note: this serializer is always nested

    genomic_interpretations = GenomicInterpretationSerializer(many=True, required=False)

    class Meta:
        model = Diagnosis
        fields = '__all__'


class InterpretationSerializer(GenericSerializer):
    # Note: this serializer is always nested

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
    # Note: this serializer is always nested

    phenotypic_features = PhenotypicFeatureSerializer(read_only=True, many=True)
    interpretations = InterpretationSerializer(many=True, required=False)
    diseases = DiseaseSerializer(many=True, required=False)

    class Meta:
        model = Phenopacket
        exclude = ("subject",)

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

    class Meta:
        model = Phenopacket
        fields = '__all__'

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
