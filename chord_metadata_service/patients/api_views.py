from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.settings import api_settings
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import IndividualSerializer
from .models import Individual
from .filters import IndividualFilter, PublicIndividualFilter
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
    queryset = Individual.objects.all().prefetch_related(
        *(f"biosamples__{p}" for p in BIOSAMPLE_PREFETCH),
        *(f"phenopackets__{p}" for p in PHENOPACKET_PREFETCH if p != "subject"),
    ).order_by("id")
    serializer_class = IndividualSerializer
    pagination_class = LargeResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, FHIRRenderer,
                        PhenopacketsRenderer, IndividualCSVRenderer, ARGORenderer)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filter_class = IndividualFilter
    ordering_fields = ["id"]

    # Cache page for the requested url, default to 2 hours.
    @method_decorator(cache_page(settings.CACHE_TIME))
    def dispatch(self, *args, **kwargs):
        return super(IndividualViewSet, self).dispatch(*args, **kwargs)


class PublicListIndividuals(APIView):
    """
    View to return only count of all individuals after filtering.
    """
    filter_backends = [DjangoFilterBackend, ]
    filter_class = PublicIndividualFilter

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request, *args, **kwargs):
        if not settings.CONFIG_PUBLIC:
            return Response(settings.NO_PUBLIC_DATA_AVAILABLE)

        base_qs = Individual.objects.all()
        filtered_qs = self.filter_queryset(base_qs)

        if filtered_qs.count() >= settings.CONFIG_PUBLIC["rules"]["count_threshold"]:
            return Response({"count": filtered_qs.count()})
        else:
            # the count < threshold when there is no match in db the queryset is empty, count = 0
            return Response(settings.INSUFFICIENT_DATA_AVAILABLE)
