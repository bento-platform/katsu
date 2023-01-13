from rest_framework import viewsets, filters, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.settings import api_settings
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from bento_lib.responses import errors

from .serializers import IndividualSerializer
from .models import Individual
from .filters import IndividualFilter
from chord_metadata_service.phenopackets.api_views import BIOSAMPLE_PREFETCH, PHENOPACKET_PREFETCH
from chord_metadata_service.restapi.api_renderers import (
    FHIRRenderer,
    PhenopacketsRenderer,
    IndividualCSVRenderer,
)
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination, BatchResultsSetPagination
from chord_metadata_service.restapi.utils import (
    get_field_options,
    filter_queryset_field_value
)
from chord_metadata_service.restapi.negociation import FormatInPostContentNegotiation
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


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
                        PhenopacketsRenderer, IndividualCSVRenderer)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = IndividualFilter
    ordering_fields = ["id"]
    search_fields = ["sex", "ethnicity"]
    queryset = Individual.objects.all().prefetch_related(
        *(f"biosamples__{p}" for p in BIOSAMPLE_PREFETCH),
        *(f"phenopackets__{p}" for p in PHENOPACKET_PREFETCH if p != "subject"),
    ).order_by("id")

    # Cache page for the requested url, default to 2 hours.

    @method_decorator(cache_page(settings.CACHE_TIME))
    def dispatch(self, *args, **kwargs):
        return super(IndividualViewSet, self).dispatch(*args, **kwargs)


class BatchViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    A viewset that only implements the 'list' action.
    To be used with the BatchListRouter which maps the POST method to .list()
    """
    pass


class IndividualBatchViewSet(BatchViewSet):

    serializer_class = IndividualSerializer
    pagination_class = BatchResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, FHIRRenderer,
                        PhenopacketsRenderer, IndividualCSVRenderer)
    # Override to infer the renderer based on a `format` argument from the POST request body
    content_negotiation_class = FormatInPostContentNegotiation

    def get_queryset(self):
        individual_id = self.request.data.get("id", None)
        filter_by_id = {"id__in": individual_id} if individual_id else {}
        queryset = Individual.objects.filter(**filter_by_id)\
            .prefetch_related(
                *(f"phenopackets__{p}" for p in PHENOPACKET_PREFETCH if p != "subject"),
        ).order_by("id")

        return queryset


@extend_schema(
    description="Individual list available in public endpoint",
    responses={
        200: inline_serializer(
            name='PublicListIndividuals_response',
            fields={
                'count': serializers.JSONField(),
            }
        )
    }
)
class PublicListIndividuals(APIView):
    """
    View to return only count of all individuals after filtering.
    """

    def filter_queryset(self, queryset):
        # Check query parameters validity
        qp = self.request.query_params
        if len(qp) > settings.CONFIG_PUBLIC["rules"]["max_query_parameters"]:
            raise ValidationError(f"Wrong number of fields: {len(qp)}")

        search_conf = settings.CONFIG_PUBLIC["search"]
        field_conf = settings.CONFIG_PUBLIC["fields"]
        queryable_fields = {
            f"{f}": field_conf[f] for section in search_conf for f in section["fields"]
        }

        for field, value in qp.items():
            if field not in queryable_fields:
                raise ValidationError(f"Unsupported field used in query: {field}")

            field_props = queryable_fields[field]
            options = get_field_options(field_props)
            if value not in options \
                    and not (
                        # case insensitive search on categories
                        field_props["datatype"] == "string"
                        and value.lower() in [o.lower() for o in options]
                    ) \
                    and not (
                        # no restriction when enum is not set for categories
                        field_props["datatype"] == "string"
                        and field_props["config"]["enum"] is None
                    ):
                raise ValidationError(f"Invalid value used in query: {value}")

            # recursion
            queryset = filter_queryset_field_value(queryset, field_props, value)

        return queryset

    def get(self, request, *args, **kwargs):
        if not settings.CONFIG_PUBLIC:
            return Response(settings.NO_PUBLIC_DATA_AVAILABLE)

        base_qs = Individual.objects.all()
        try:
            filtered_qs = self.filter_queryset(base_qs)
        except ValidationError as e:
            return Response(errors.bad_request_error(
                *(e.error_list if hasattr(e, "error_list") else e.error_dict.items()),
            ))

        if filtered_qs.count() > settings.CONFIG_PUBLIC["rules"]["count_threshold"]:
            return Response({"count": filtered_qs.count()})
        else:
            # the count < threshold when there is no match in db the queryset is empty, count = 0
            return Response(settings.INSUFFICIENT_DATA_AVAILABLE)
