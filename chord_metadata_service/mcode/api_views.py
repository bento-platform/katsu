from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .schemas import MCODE_SCHEMA
from . import models as m, serializers as s
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer, ARGORenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination


class McodeModelViewSet(viewsets.ModelViewSet):
    pagination_class = LargeResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)

    # Cache page for the requested url for 2 hours
    @method_decorator(cache_page(60 * 60 * 2))
    def dispatch(self, *args, **kwargs):
        return super(McodeModelViewSet, self).dispatch(*args, **kwargs)


class GeneticSpecimenViewSet(McodeModelViewSet):
    queryset = m.GeneticSpecimen.objects.all()
    serializer_class = s.GeneticSpecimenSerializer
    renderer_classes = tuple(McodeModelViewSet.renderer_classes) + (ARGORenderer,)


class CancerGeneticVariantViewSet(McodeModelViewSet):
    queryset = m.CancerGeneticVariant.objects.all()
    serializer_class = s.CancerGeneticVariantSerializer


class GenomicRegionStudiedViewSet(McodeModelViewSet):
    queryset = m.GenomicRegionStudied.objects.all()
    serializer_class = s.GenomicRegionStudiedSerializer


GENOMIC_REPORT_PREFETCH = (
    "genetic_specimen",
    "genomic_region_studied",
)

GENOMIC_REPORT_SELECT = (
    "genetic_variant",
)


class GenomicsReportViewSet(McodeModelViewSet):
    queryset = m.GenomicsReport.objects.all()
    serializer_class = s.GenomicsReportSerializer


class LabsVitalViewSet(McodeModelViewSet):
    queryset = m.LabsVital.objects.all()
    serializer_class = s.LabsVitalSerializer


CANCER_CONDITION_PREFETCH = (
    "tnmstaging_set",
)


class CancerConditionViewSet(McodeModelViewSet):
    queryset = m.CancerCondition.objects.all()
    serializer_class = s.CancerConditionSerializer
    renderer_classes = tuple(McodeModelViewSet.renderer_classes) + (ARGORenderer,)


class TNMStagingViewSet(McodeModelViewSet):
    queryset = m.TNMStaging.objects.all()
    serializer_class = s.TNMStagingSerializer


CANCER_RELATED_PROCEDURE = (
    "reason_reference",
)


class CancerRelatedProcedureViewSet(McodeModelViewSet):
    queryset = m.CancerRelatedProcedure.objects.all()
    serializer_class = s.CancerRelatedProcedureSerializer
    renderer_classes = tuple(McodeModelViewSet.renderer_classes) + (ARGORenderer,)


class MedicationStatementViewSet(McodeModelViewSet):
    queryset = m.MedicationStatement.objects.all()
    serializer_class = s.MedicationStatementSerializer
    renderer_classes = tuple(McodeModelViewSet.renderer_classes) + (ARGORenderer,)


MCODEPACKET_PREFETCH = (
    "cancer_condition",
    "cancer_related_procedures",
    "medication_statement",
)

MCODEPACKET_SELECT = (
    "subject",
    "genomics_report",
)


class MCodePacketViewSet(McodeModelViewSet):
    queryset = m.MCodePacket.objects.all()\
        .prefetch_related(*MCODEPACKET_PREFETCH)\
        .select_related(*MCODEPACKET_SELECT)\
        .order_by("id")
    serializer_class = s.MCodePacketSerializer
    renderer_classes = tuple(McodeModelViewSet.renderer_classes) + (ARGORenderer,)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_mcode_schema(_request):
    """
    get:
    Mcodepacket schema
    """
    return Response(MCODE_SCHEMA)
