from rest_framework import serializers
from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import *


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