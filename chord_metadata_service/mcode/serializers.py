from chord_metadata_service.restapi.serializers import GenericSerializer
from chord_metadata_service.patients.serializers import IndividualSerializer
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
    genetic_variant_tested = GeneticVariantTestedSerializer(read_only=True, many=True)
    genetic_variant_found = GeneticVariantTestedSerializer(read_only=True, many=True)

    class Meta:
        model = GenomicsReport
        fields = '__all__'


class LabsVitalSerializer(GenericSerializer):

    class Meta:
        model = LabsVital
        fields = '__all__'


class TNMStagingSerializer(GenericSerializer):

    class Meta:
        model = TNMStaging
        fields = '__all__'


class CancerConditionSerializer(GenericSerializer):
    tnm_staging = TNMStagingSerializer(source='tnmstaging_set', read_only=True, many=True)

    class Meta:
        model = CancerCondition
        fields = '__all__'


class CancerRelatedProcedureSerializer(GenericSerializer):

    class Meta:
        model = CancerRelatedProcedure
        fields = '__all__'


class MedicationStatementSerializer(GenericSerializer):

    class Meta:
        model = MedicationStatement
        fields = '__all__'


class MCodePacketSerializer(GenericSerializer):
    subject = IndividualSerializer()
    genomics_report = GenomicsReportSerializer()
    cancer_condition = CancerConditionSerializer()
    cancer_related_procedures = CancerRelatedProcedureSerializer(many=True)
    medication_statement = MedicationStatementSerializer()

    class Meta:
        model = MCodePacket
        fields = '__all__'
