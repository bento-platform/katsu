from rest_framework import viewsets
from rest_framework.settings import api_settings
from .serializers import *
from chord_metadata_service.restapi.api_renderers import (
    PhenopacketsRenderer
)
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination


class McodeModelViewSet(viewsets.ModelViewSet):
    pagination_class = LargeResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)


class GeneticVariantTestedViewSet(McodeModelViewSet):
    queryset = GeneticVariantTested.objects.all().order_by("id")
    serializer_class = GeneticVariantTestedSerializer


class GeneticVariantFoundViewSet(McodeModelViewSet):
    queryset = GeneticVariantFound.objects.all().order_by("id")
    serializer_class = GeneticVariantFoundSerializer


class GenomicsReportViewSet(McodeModelViewSet):
    queryset = GenomicsReport.objects.all().order_by("id")
    serializer_class = GenomicsReportSerializer


class LabsVitalViewSet(McodeModelViewSet):
    queryset = LabsVital.objects.all().order_by("id")
    serializer_class = LabsVitalSerializer


class CancerConditionViewSet(McodeModelViewSet):
    queryset = CancerCondition.objects.all().order_by("id")
    serializer_class = CancerConditionSerializer


class TNMStagingViewSet(McodeModelViewSet):
    queryset = TNMStaging.objects.all().order_by("id")
    serializer_class = TNMStagingSerializer


class CancerRelatedProcedureViewSet(McodeModelViewSet):
    queryset = CancerRelatedProcedure.objects.all().order_by("id")
    serializer_class = CancerRelatedProcedureSerializer


class MedicationStatementViewSet(McodeModelViewSet):
    queryset = MedicationStatement.objects.all().order_by("id")
    serializer_class = MedicationStatementSerializer

