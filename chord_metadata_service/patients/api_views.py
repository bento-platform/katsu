from rest_framework import viewsets, filters
from rest_framework.settings import api_settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import IndividualSerializer, ListIndividualSerializer
from .models import Individual
from .filters import IndividualFilter
from chord_metadata_service.phenopackets.api_views import BIOSAMPLE_PREFETCH, PHENOPACKET_PREFETCH
from chord_metadata_service.restapi.api_renderers import FHIRRenderer, PhenopacketsRenderer, IndividualCSVRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination


class IndividualViewSet(viewsets.ModelViewSet):
    """
    get:
    Return a list of all existing individuals

    post:
    Create a new individual

    """
    queryset = Individual.objects.all().prefetch_related(
        *(f"biosamples__{p}" for p in BIOSAMPLE_PREFETCH),
        *(f"phenopackets__{p}" for p in PHENOPACKET_PREFETCH if p != "subject"),
    ).order_by("id")
    serializer_class = IndividualSerializer
    pagination_class = LargeResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, FHIRRenderer,
                        PhenopacketsRenderer, IndividualCSVRenderer)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filter_class = IndividualFilter
    ordering_fields = ["id"]

    def list(self, request):
        queryset = Individual.objects.all()
        # apply filtering
        filtered_queryset = self.filter_queryset(queryset)
        # paginate
        paginated_queryset = self.paginate_queryset(filtered_queryset)
        serializer = ListIndividualSerializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    # Cache page for the requested url for 2 hours
    @method_decorator(cache_page(60*60*2))
    def dispatch(self, *args, **kwargs):
        return super(IndividualViewSet, self).dispatch(*args, **kwargs)
