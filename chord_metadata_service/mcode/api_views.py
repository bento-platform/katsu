from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import *
from .schemas import MCODE_SCHEMA
from .models import *
from .serializers import *
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination


class McodeModelViewSet(viewsets.ModelViewSet):
    pagination_class = LargeResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)


class GeneticSpecimenViewSet(McodeModelViewSet):
    queryset = GeneticSpecimen.objects.all()
    serializer_class = GeneticSpecimenSerializer


class CancerGeneticVariantViewSet(McodeModelViewSet):
    queryset = CancerGeneticVariant.objects.all()
    serializer_class = CancerGeneticVariantSerializer


class GenomicRegionStudiedViewSet(McodeModelViewSet):
    queryset = GenomicRegionStudied.objects.all()
    serializer_class = GenomicRegionStudiedSerializer


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


@api_view(["GET"])
@permission_classes([AllowAny])
def get_mcode_schema(_request):
    """
    get:
    Mcodepacket schema
    """
    return Response(MCODE_SCHEMA)
