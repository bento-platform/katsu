from rest_framework import viewsets, filters
from rest_framework.settings import api_settings
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import IndividualSerializer
from .models import Individual
from .filters import IndividualFilter
from chord_metadata_service.phenopackets.api_views import BIOSAMPLE_PREFETCH, PHENOPACKET_PREFETCH
from chord_metadata_service.restapi.api_renderers import (
    FHIRRenderer,
    PhenopacketsRenderer,
    IndividualCSVRenderer,
    ARGORenderer,
)
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination


class IndividualViewSet(viewsets.ModelViewSet):
    """
    get:
    Return a list of all existing individuals

    post:
    Create a new individual

    """
    serializer_class = IndividualSerializer
    pagination_class = LargeResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, FHIRRenderer,
                        PhenopacketsRenderer, IndividualCSVRenderer, ARGORenderer)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filter_class = IndividualFilter
    ordering_fields = ["id"]
    search_fields = ["sex", "ethnicity"]

    def get_queryset(self):
        if hasattr(self.request, "allowed_datasets"):
            allowed_datasets = self.request.allowed_datasets
            queryset = Individual.objects.\
                filter(phenopackets__table__ownership_record__dataset__title__in=allowed_datasets).\
                prefetch_related(*(f"biosamples__{p}" for p in BIOSAMPLE_PREFETCH),
                                 *(f"phenopackets__{p}" for p in PHENOPACKET_PREFETCH if p != "subject")).\
                order_by("id")
        else:
            queryset = Individual.objects.all().prefetch_related(
                *(f"biosamples__{p}" for p in BIOSAMPLE_PREFETCH),
                *(f"phenopackets__{p}" for p in PHENOPACKET_PREFETCH if p != "subject"),
            ).order_by("id")
        return queryset

    # Cache page for the requested url, default to 2 hours.
    @method_decorator(cache_page(settings.CACHE_TIME))
    def dispatch(self, *args, **kwargs):
        return super(IndividualViewSet, self).dispatch(*args, **kwargs)
