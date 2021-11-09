from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .schemas import MCODE_SCHEMA
from . import models as m, serializers as s
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination


class McodeModelViewSet(viewsets.ModelViewSet):
    pagination_class = LargeResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)

    def dispatch(self, *args, **kwargs):
        return super(McodeModelViewSet, self).dispatch(*args, **kwargs)


class GeneticSpecimenViewSet(McodeModelViewSet):
    serializer_class = s.GeneticSpecimenSerializer

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

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.GenomicRegionStudied.objects\
                .filter(genomicsreport__mcodepacket__table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.GenomicRegionStudied.objects.all()
        return queryset

class GenomicsReportViewSet(McodeModelViewSet):
    serializer_class = s.GenomicsReportSerializer

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

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.LabsVital.objects\
                .filter(individual__mcodepacket__table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.LabsVital.objects.all()
        return queryset


class CancerConditionViewSet(McodeModelViewSet):
    serializer_class = s.CancerConditionSerializer

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

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.TNMStaging.objects\
                .filter(cancer_condition__mcodepacket__table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.TNMStaging.objects.all()
        return queryset



class CancerRelatedProcedureViewSet(McodeModelViewSet):
    serializer_class = s.CancerRelatedProcedureSerializer

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

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = m.MedicationStatement.objects\
                .filter(mcodepacket__table__ownership_record__dataset__title__in=allowed_datasets)
        else:
            queryset = m.MedicationStatement.objects.all()
        return queryset


class MCodePacketViewSet(McodeModelViewSet):
    serializer_class = s.MCodePacketSerializer

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
