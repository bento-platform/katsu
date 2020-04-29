from rest_framework import viewsets
from rest_framework.settings import api_settings
from .models import *
from .serializers import *
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination


class McodeModelViewSet(viewsets.ModelViewSet):
    pagination_class = LargeResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)


class GeneticVariantTestedViewSet(McodeModelViewSet):
    queryset = GeneticVariantTested.objects.all()
    serializer_class = GeneticVariantTestedSerializer


class GeneticVariantFoundViewSet(McodeModelViewSet):
    queryset = GeneticVariantFound.objects.all()
    serializer_class = GeneticVariantFoundSerializer


class GenomicsReportViewSet(McodeModelViewSet):
    queryset = GenomicsReport.objects.all()
    serializer_class = GenomicsReportSerializer


class LabsVitalViewSet(McodeModelViewSet):
    queryset = LabsVital.objects.all()
    serializer_class = LabsVitalSerializer


class CancerConditionViewSet(McodeModelViewSet):
    queryset = CancerCondition.objects.all()
    serializer_class = CancerConditionSerializer


class TNMStagingViewSet(McodeModelViewSet):
    queryset = TNMStaging.objects.all()
    serializer_class = TNMStagingSerializer


class CancerRelatedProcedureViewSet(McodeModelViewSet):
    queryset = CancerRelatedProcedure.objects.all()
    serializer_class = CancerRelatedProcedureSerializer


class MedicationStatementViewSet(McodeModelViewSet):
    queryset = MedicationStatement.objects.all()
    serializer_class = MedicationStatementSerializer


class MCodePacketViewSet(McodeModelViewSet):
    queryset = MCodePacket.objects.all()
    serializer_class = MCodePacketSerializer
