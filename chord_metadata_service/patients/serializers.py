from chord_metadata_service.phenopackets.serializers import (
    BiosampleSerializer, SimplePhenopacketSerializer, ListPhenopacketSerializer
)
from chord_metadata_service.restapi.serializers import GenericSerializer
from chord_metadata_service.restapi.fhir_utils import fhir_patient
from .models import Individual
from rest_framework import serializers


class IndividualSerializer(GenericSerializer):
    biosamples = BiosampleSerializer(read_only=True, many=True, exclude_when_nested=['individual'])
    phenopackets = SimplePhenopacketSerializer(read_only=True, many=True, exclude_when_nested=['subject'])

    class Meta:
        model = Individual
        fields = "__all__"
        # meta info for converting to FHIR
        fhir_datatype_plural = 'patients'
        class_converter = fhir_patient


class ListIndividualSerializer(GenericSerializer):
    biosamples = serializers.SerializerMethodField()
    experiments = serializers.SerializerMethodField()

    class Meta:
        model = Individual
        fields = ['id', 'alternate_ids', 'date_of_birth', 'age', 'sex', 'karyotypic_sex', 'taxonomy',
                  'active', 'deceased', 'comorbid_condition', 'ecog_performance_status', 'karnofsky',
                  'race', 'ethnicity', 'extra_properties', 'created', 'updated', 'biosamples', 'experiments']
        # meta info for converting to FHIR
        fhir_datatype_plural = 'patients'
        class_converter = fhir_patient

    def get_biosamples(self, obj):
        return [b.id for p in obj.phenopackets.all() for b in p.biosamples.all()]

    def get_experiments(self, obj):
        return [exp.id for p in obj.phenopackets.all() for b in p.biosamples.all() for exp in b.experiment_set.all()]
