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
    filter_class = f.GeneticSpecimenFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.GeneticSpecimen.objects\
                .filter(genomicsreport__mcodepacket__table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.GeneticSpecimen.objects.all()
        return queryset


class CancerGeneticVariantViewSet(McodeModelViewSet):
    serializer_class = s.CancerGeneticVariantSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.CancerGeneticVariantFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.CancerGeneticVariant.objects\
                .filter(genomicsreport__mcodepacket__table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.CancerGeneticVariant.objects.all()
        return queryset


class GenomicRegionStudiedViewSet(McodeModelViewSet):
    serializer_class = s.GenomicRegionStudiedSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.GenomicRegionStudiedFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.GenomicRegionStudied.objects\
                .filter(genomicsreport__mcodepacket__table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.GenomicRegionStudied.objects.all()
        return queryset


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
    filter_class = f.GenomicsReportFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.GenomicsReport.objects\
                .filter(mcodepacket__table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.GenomicsReport.objects.all()
        return queryset


class LabsVitalViewSet(McodeModelViewSet):
    serializer_class = s.LabsVitalSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.LabsVitalFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.LabsVital.objects\
                .filter(individual__mcodepacket__table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.LabsVital.objects.all()
        return queryset


CANCER_CONDITION_PREFETCH = (
    "tnmstaging_set",
)


class CancerConditionViewSet(McodeModelViewSet):
    serializer_class = s.CancerConditionSerializer
    renderer_classes = tuple(McodeModelViewSet.renderer_classes) + (ARGORenderer,)
    filter_backends = [DjangoFilterBackend]
    filter_class = f.CancerConditionFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.CancerCondition.objects\
                .filter(mcodepacket__table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.CancerCondition.objects.all()
        return queryset


class TNMStagingViewSet(McodeModelViewSet):
    serializer_class = s.TNMStagingSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.TNMStagingFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.TNMStaging.objects\
                .filter(cancer_condition__mcodepacket__table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.TNMStaging.objects.all()
        return queryset


CANCER_RELATED_PROCEDURE = (
    "reason_reference",
)


class CancerRelatedProcedureViewSet(McodeModelViewSet):
    serializer_class = s.CancerRelatedProcedureSerializer
    renderer_classes = tuple(McodeModelViewSet.renderer_classes) + (ARGORenderer,)
    filter_backends = [DjangoFilterBackend]
    filter_class = f.CancerRelatedProcedureFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.CancerRelatedProcedure.objects\
                .filter(mcodepacket__table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.CancerRelatedProcedure.objects.all()
        return queryset


class MedicationStatementViewSet(McodeModelViewSet):
    serializer_class = s.MedicationStatementSerializer
    renderer_classes = tuple(McodeModelViewSet.renderer_classes) + (ARGORenderer,)
    filter_backends = [DjangoFilterBackend]
    filter_class = f.MedicationStatementFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.MedicationStatement.objects\
                .filter(mcodepacket__table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.MedicationStatement.objects.all()
        return queryset


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
    filter_class = f.MCodePacketFilter

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.MCodePacket.objects\
                .filter(table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.MCodePacket.objects.all()
        return queryset


@api_view(["GET"])
@permission_classes([AllowAny])
def get_mcode_schema(_request):
    """
    get:
    Mcodepacket schema
    """
    return Response(MCODE_SCHEMA)
