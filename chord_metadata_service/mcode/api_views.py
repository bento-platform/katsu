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
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination


class McodeModelViewSet(viewsets.ModelViewSet):
    pagination_class = LargeResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)

    # Cache response to the requested URL, default to 2 hours.
    @method_decorator(cache_page(settings.CACHE_TIME))
    def dispatch(self, *args, **kwargs):
        return super(McodeModelViewSet, self).dispatch(*args, **kwargs)


class GeneticSpecimenViewSet(McodeModelViewSet):
    queryset = m.GeneticSpecimen.objects.all()
    serializer_class = s.GeneticSpecimenSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.GeneticSpecimenFilter


class CancerGeneticVariantViewSet(McodeModelViewSet):
    queryset = m.CancerGeneticVariant.objects.all()
    serializer_class = s.CancerGeneticVariantSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.CancerGeneticVariantFilter


class GenomicRegionStudiedViewSet(McodeModelViewSet):
    queryset = m.GenomicRegionStudied.objects.all()
    serializer_class = s.GenomicRegionStudiedSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.GenomicRegionStudiedFilter


class GenomicsReportViewSet(McodeModelViewSet):
    queryset = m.GenomicsReport.objects.all()
    serializer_class = s.GenomicsReportSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.GenomicsReportFilter


class LabsVitalViewSet(McodeModelViewSet):
    queryset = m.LabsVital.objects.all()
    serializer_class = s.LabsVitalSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.LabsVitalFilter


class CancerConditionViewSet(McodeModelViewSet):
    queryset = m.CancerCondition.objects.all()
    serializer_class = s.CancerConditionSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.CancerConditionFilter


class TNMStagingViewSet(McodeModelViewSet):
    queryset = m.TNMStaging.objects.all()
    serializer_class = s.TNMStagingSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.TNMStagingFilter


class CancerRelatedProcedureViewSet(McodeModelViewSet):
    queryset = m.CancerRelatedProcedure.objects.all()
    serializer_class = s.CancerRelatedProcedureSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.CancerRelatedProcedureFilter


class MedicationStatementViewSet(McodeModelViewSet):
    queryset = m.MedicationStatement.objects.all()
    serializer_class = s.MedicationStatementSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.MedicationStatementFilter


class MCodePacketViewSet(McodeModelViewSet):
    queryset = m.MCodePacket.objects.all()
    serializer_class = s.MCodePacketSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.MCodePacketFilter


@api_view(["GET"])
@permission_classes([AllowAny])
def get_mcode_schema(_request):
    """
    get:
    Mcodepacket schema
    """
    return Response(MCODE_SCHEMA)
    