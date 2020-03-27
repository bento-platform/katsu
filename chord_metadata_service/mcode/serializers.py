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

    class Meta:
        model = GenomicsReport
        fields = '__all__'

    def to_representation(self, instance):
        """"
        Overriding this method to allow post Primary Key for FK and M2M
        objects and return their nested serialization.
        """
        response = super().to_representation(instance)
        response['genetic_variant_tested'] = GeneticVariantTestedSerializer(instance.genetic_variant_tested,
                                                                            many=True, required=False).data
        response['genetic_variant_found'] = GeneticVariantFoundSerializer(instance.genetic_variant_found,
                                                                           many=True, required=False).data
        return response


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

    def to_representation(self, instance):
        """"
        Overriding this method to allow post Primary Key for FK and M2M
        objects and return their nested serialization.
        """
        response = super().to_representation(instance)
        response['subject'] = IndividualSerializer(instance.subject).data
        response['genomics_report'] = GenomicsReportSerializer(instance.genomics_report, required=False).data
        response['cancer_condition'] = CancerConditionSerializer(instance.cancer_condition, required=False).data
        response['cancer_related_procedures'] = CancerRelatedProcedureSerializer(instance.cancer_related_procedures,
                                                                                 many=True, required=False).data
        response['medication_statement'] = MedicationStatementSerializer(instance.medication_statement,
                                                                         required=False).data
        return response

    class Meta:
        model = MCodePacket
        fields = '__all__'
