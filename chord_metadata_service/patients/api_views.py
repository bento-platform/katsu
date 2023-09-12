import re

from datetime import datetime

from rest_framework import viewsets, filters, mixins, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from django.db.models import Count, F, Q
from django.db.models.functions import Coalesce
from django.contrib.postgres.aggregates import ArrayAgg
from drf_spectacular.utils import extend_schema, inline_serializer
from bento_lib.responses import errors
from bento_lib.search import build_search_response

from .serializers import IndividualSerializer
from .models import Individual
from .filters import IndividualFilter
from chord_metadata_service.logger import logger
from chord_metadata_service.phenopackets.api_views import BIOSAMPLE_PREFETCH, PHENOPACKET_PREFETCH
from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.phenopackets.serializers import PhenopacketSerializer
from chord_metadata_service.restapi.api_renderers import (
    FHIRRenderer,
    PhenopacketsRenderer,
    IndividualCSVRenderer,
    ARGORenderer,
    IndividualBentoSearchRenderer,
)
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination, BatchResultsSetPagination
from chord_metadata_service.restapi.utils import (
    get_field_options,
    filter_queryset_field_value,
    biosample_tissue_stats,
    experiment_type_stats
)
from chord_metadata_service.restapi.negociation import FormatInPostContentNegotiation


OUTPUT_FORMAT_BENTO_SEARCH_RESULT = "bento_search_result"


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
                        PhenopacketsRenderer, IndividualCSVRenderer, ARGORenderer,
                        IndividualBentoSearchRenderer)
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

    def list(self, request, *args, **kwargs):
        if request.query_params.get("format") == OUTPUT_FORMAT_BENTO_SEARCH_RESULT:
            start = datetime.now()
            # filterset applies filtering from the GET parameters
            filterset = self.filterset_class(request.query_params, queryset=self.queryset)
            # Note: it is necessary here to use a second queryset because
            # filterset is a queryset containing a `distinct()` method which
            # is incompatible with the annotations defined bellow.
            # (in SQL the DISTINCT clause is not compatible with GROUP BY statements
            # which serve a similar purpose)
            individual_ids = filterset.qs.values_list("id", flat=True)
            # TODO: code duplicated from chord/view_search.py
            qs = Phenopacket.objects.filter(subject__id__in=individual_ids).values(
                "subject_id",
                alternate_ids=Coalesce(F("subject__alternate_ids"), [])
            ).annotate(
                num_experiments=Count("biosamples__experiment"),
                biosamples=Coalesce(
                    ArrayAgg("biosamples__id", distinct=True, filter=Q(biosamples__id__isnull=False)),
                    []
                )
            )
            return Response(build_search_response(list(qs), start))

        return super(IndividualViewSet, self).list(request, *args, **kwargs)

    @action(detail=True, methods=["GET"])
    def phenopackets(self, request, *_args, **_kwargs):
        as_attachment = request.query_params.get("attachment", "") in ("1", "true", "yes")
        individual = self.get_object()

        phenopackets = (
            Phenopacket.objects
            .filter(subject=individual)
            .prefetch_related(*PHENOPACKET_PREFETCH)
            .order_by("id")
        )

        filename_safe_id = re.sub(r"[\\/:*?\"<>|]", "_", individual.id)
        return Response(
            PhenopacketSerializer(phenopackets, many=True).data,
            headers=(
                {"Content-Disposition": f"attachment; filename=\"{filename_safe_id}_phenopackets.json\""}
                if as_attachment else {}
            ),
        )


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
                        PhenopacketsRenderer, IndividualCSVRenderer, ARGORenderer,
                        IndividualBentoSearchRenderer)
    # Override to infer the renderer based on a `format` argument from the POST request body
    content_negotiation_class = FormatInPostContentNegotiation

    def get_queryset(self):
        individual_ids = self.request.data.get("id", None)
        filter_by_id = {"id__in": individual_ids} if individual_ids else {}
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
                        # case-insensitive search on categories
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

        qct = filtered_qs.count()

        if qct <= (threshold := settings.CONFIG_PUBLIC["rules"]["count_threshold"]):
            logger.info(
                f"Public individuals endpoint recieved query params {request.query_params} which resulted in "
                f"sub-threshold count: {qct} <= {threshold}")
            return Response(settings.INSUFFICIENT_DATA_AVAILABLE)

        tissues_count, sampled_tissues = biosample_tissue_stats(filtered_qs)
        experiments_count, experiment_types = experiment_type_stats(filtered_qs)

        return Response({
            "count": qct,
            "biosamples": {
                "count": tissues_count,
                "sampled_tissue": sampled_tissues
            },
            "experiments": {
                "count": experiments_count,
                "experiment_type": experiment_types
            }
        })


class BeaconListIndividuals(APIView):
    """
    View to return lists of individuals filtered using search terms from katsu's config.json.
    Uncensored equivalent of PublicListIndividuals.
    """
    def filter_queryset(self, queryset):
        # Check query parameters validity
        qp = self.request.query_params
        if len(qp) > settings.CONFIG_PUBLIC["rules"]["max_query_parameters"]:
            raise ValidationError(f"Wrong number of fields: {len(qp)}")

        search_conf = settings.CONFIG_PUBLIC["search"]
        field_conf = settings.CONFIG_PUBLIC["fields"]
        queryable_fields = {
            f: field_conf[f] for section in search_conf for f in section["fields"]
        }

        for field, value in qp.items():
            if field not in queryable_fields:
                raise ValidationError(f"Unsupported field used in query: {field}")

            field_props = queryable_fields[field]
            options = get_field_options(field_props)
            if value not in options \
                    and not (
                        # case-insensitive search on categories
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
            return Response(settings.NO_PUBLIC_DATA_AVAILABLE, status=404)

        base_qs = Individual.objects.all()
        try:
            filtered_qs = self.filter_queryset(base_qs)
        except ValidationError as e:
            return Response(errors.bad_request_error(
                *(e.error_list if hasattr(e, "error_list") else e.error_dict.items())), status=400)

        tissues_count, sampled_tissues = biosample_tissue_stats(filtered_qs)
        experiments_count, experiment_types = experiment_type_stats(filtered_qs)

        return Response({
            "matches": filtered_qs.values_list("id", flat=True),
            "biosamples": {
                "count": tissues_count,
                "sampled_tissue": sampled_tissues
            },
            "experiments": {
                "count": experiments_count,
                "experiment_type": experiment_types
            }
        })
