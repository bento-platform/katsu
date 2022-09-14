from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend

from .schemas import MCODE_SCHEMA

from . import models as m, serializers as s, filters as f
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer, ARGORenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


class McodeModelViewSet(viewsets.ModelViewSet):
    pagination_class = LargeResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)

    # Cache response to the requested URL, default to 2 hours.
    @method_decorator(cache_page(settings.CACHE_TIME))
    def dispatch(self, *args, **kwargs):
        return super(McodeModelViewSet, self).dispatch(*args, **kwargs)


class GeneticSpecimenViewSet(McodeModelViewSet):
    serializer_class = s.GeneticSpecimenSerializer
    renderer_classes = tuple(McodeModelViewSet.renderer_classes) + (ARGORenderer,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.GeneticSpecimenFilter
    queryset = m.GeneticSpecimen.objects.all()


class CancerGeneticVariantViewSet(McodeModelViewSet):
    serializer_class = s.CancerGeneticVariantSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.CancerGeneticVariantFilter
    queryset = m.CancerGeneticVariant.objects.all()


class GenomicRegionStudiedViewSet(McodeModelViewSet):
    serializer_class = s.GenomicRegionStudiedSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.GenomicRegionStudiedFilter
    queryset = m.GenomicRegionStudied.objects.all()


GENOMIC_REPORT_PREFETCH = (
    "genetic_specimen",
    "genomic_region_studied",
)

GENOMIC_REPORT_SELECT = (
    "genetic_variant",
)


class GenomicsReportViewSet(McodeModelViewSet):
    serializer_class = s.GenomicsReportSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.GenomicsReportFilter
    queryset = m.GenomicsReport.objects.all()


class LabsVitalViewSet(McodeModelViewSet):
    serializer_class = s.LabsVitalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.LabsVitalFilter
    queryset = m.LabsVital.objects.all()


CANCER_CONDITION_PREFETCH = (
    "tnmstaging_set",
)


class CancerConditionViewSet(McodeModelViewSet):
    serializer_class = s.CancerConditionSerializer
    renderer_classes = tuple(McodeModelViewSet.renderer_classes) + (ARGORenderer,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.CancerConditionFilter
    queryset = m.CancerCondition.objects.all()


class TNMStagingViewSet(McodeModelViewSet):
    serializer_class = s.TNMStagingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.TNMStagingFilter
    queryset = m.TNMStaging.objects.all()


CANCER_RELATED_PROCEDURE = (
    "reason_reference",
)


class CancerRelatedProcedureViewSet(McodeModelViewSet):
    serializer_class = s.CancerRelatedProcedureSerializer
    renderer_classes = tuple(McodeModelViewSet.renderer_classes) + (ARGORenderer,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.CancerRelatedProcedureFilter
    queryset = m.CancerRelatedProcedure.objects.all()


class MedicationStatementViewSet(McodeModelViewSet):
    serializer_class = s.MedicationStatementSerializer
    renderer_classes = tuple(McodeModelViewSet.renderer_classes) + (ARGORenderer,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.MedicationStatementFilter
    queryset = m.MedicationStatement.objects.all()


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
    serializer_class = s.MCodePacketSerializer
    renderer_classes = tuple(McodeModelViewSet.renderer_classes) + (ARGORenderer,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = f.MCodePacketFilter
    queryset = m.MCodePacket.objects.all()


@extend_schema(
    description="Mcodepacket schema",
    responses={
        200: inline_serializer(
            name='mcode_schema_response',
            fields={
                'MCODE_SCHEMA': serializers.JSONField(),
            }
        )
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_mcode_schema(_request):
    """
    get:
    Mcodepacket schema
    """
    return Response(MCODE_SCHEMA)
