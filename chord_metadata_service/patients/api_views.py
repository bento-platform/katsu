import asyncio
import re

from asgiref.sync import async_to_sync
from datetime import datetime
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from bento_lib.responses.errors import forbidden_error
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from django.db.models import Count, F, Q, QuerySet
from django.db.models.functions import Coalesce
from django.contrib.postgres.aggregates import ArrayAgg
from drf_spectacular.utils import extend_schema, inline_serializer
from bento_lib.responses import errors
from bento_lib.search import build_search_response

from chord_metadata_service.authz.discovery import DataTypeDiscoveryPermissions
from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.discovery.censorship import thresholded_count
from chord_metadata_service.discovery.fields import get_field_options, filter_queryset_field_value
from chord_metadata_service.discovery.stats import biosample_tissue_stats, experiment_type_stats
from chord_metadata_service.discovery.helpers import (
    get_public_data_type_permissions,
    get_public_queryable_fields,
    get_discovery_rules_and_field_set_permissions,
)
from chord_metadata_service.restapi.api_renderers import (
    FHIRRenderer,
    PhenopacketsRenderer,
    IndividualCSVRenderer,
    ARGORenderer,
    IndividualBentoSearchRenderer,
)
from chord_metadata_service.phenopackets.api_views import BIOSAMPLE_PREFETCH, PHENOPACKET_PREFETCH
from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.phenopackets.serializers import PhenopacketSerializer
from chord_metadata_service.restapi.constants import MODEL_ID_PATTERN
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination, BatchResultsSetPagination
from chord_metadata_service.restapi.negociation import FormatInPostContentNegotiation

from .serializers import IndividualSerializer
from .models import Individual
from .filters import IndividualFilter

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
    search_fields = ["sex"]
    queryset = Individual.objects.all().prefetch_related(
        *(f"biosamples__{p}" for p in BIOSAMPLE_PREFETCH),
        *(f"phenopackets__{p}" for p in PHENOPACKET_PREFETCH if p != "subject"),
    ).order_by("id")
    lookup_value_regex = MODEL_ID_PATTERN

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

    @action(detail=True, methods=["GET", "POST"])
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


async def public_discovery_filter_queryset(
    request: DrfRequest,
    queryset: QuerySet,
    dt_permissions: DataTypeDiscoveryPermissions,
) -> QuerySet:
    # Check query parameters validity
    qp = request.query_params

    queryable_fields = get_public_queryable_fields()
    rules, all_qf_permissions, qf_permissions = get_discovery_rules_and_field_set_permissions(dt_permissions, qp.keys())

    # max_query_parameters was adjusted by get_config_public_and_field_set_permissions:
    if len(qp) > rules["max_query_parameters"]:
        raise ValidationError(f"Wrong number of fields: {len(qp)}")

    for field, value in qp.items():
        field_props = queryable_fields[field]
        options = await get_field_options(field_props, low_counts_censored=not qf_permissions[field]["data"])
        if (
            value not in options
            and not (
                # case-insensitive search on categories
                field_props["datatype"] == "string" and value.lower() in [o.lower() for o in options]
            )
            and not (
                # no restriction when enum is not set for categories
                field_props["datatype"] == "string" and field_props["config"]["enum"] is None
            )
        ):
            raise ValidationError(f"Invalid value used in query: {value}")

        # recursion
        queryset = filter_queryset_field_value(queryset, field_props, value)

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

    # TODO: should be project-scoped

    @async_to_sync
    async def get(self, request, *_args, **_kwargs):
        if not settings.CONFIG_PUBLIC:
            authz_middleware.mark_authz_done(request)
            return Response(settings.NO_PUBLIC_DATA_AVAILABLE, status=status.HTTP_404_NOT_FOUND)

        # TODO: permissions - should be project-scoped or something instead of whole-node-scroped
        # Access (counts/data) permissions by Bento data type
        dt_permissions = await get_public_data_type_permissions(request)
        dt_perms_pheno = dt_permissions[DATA_TYPE_PHENOPACKET]
        dt_perms_exp = dt_permissions[DATA_TYPE_EXPERIMENT]

        # We can't respond if we don't have at least phenopackets counts permission
        if not any(dt_perms_pheno.values()):
            authz_middleware.mark_authz_done(request)
            return Response(forbidden_error(), status=status.HTTP_403_FORBIDDEN)

        base_qs = Individual.objects.all()
        try:
            filtered_qs = await public_discovery_filter_queryset(self.request, base_qs, dt_permissions)
        except ValidationError as e:
            return Response(
                errors.bad_request_error(*(e.error_list if hasattr(e, "error_list") else e.error_dict.items())),
                status=status.HTTP_400_BAD_REQUEST,
            )

        perm_pheno_query_data = dt_perms_pheno["data"]

        ind_qct = thresholded_count(await filtered_qs.acount(), low_counts_censored=not perm_pheno_query_data)

        if ind_qct == 0 and not perm_pheno_query_data:
            # Not enough data to respond with counts
            authz_middleware.mark_authz_done(request)
            return Response(settings.INSUFFICIENT_DATA_AVAILABLE)

        (tissues_count, sampled_tissues), (experiments_count, experiment_types) = await asyncio.gather(
            biosample_tissue_stats(filtered_qs, low_counts_censored=not perm_pheno_query_data),
            experiment_type_stats(filtered_qs, low_counts_censored=not dt_perms_exp["counts"]),
        )

        # TODO: project-scoped permissions
        # We are already guaranteed to have project-level counts permission here for PHENOPACKETS ONLY
        return Response({
            "count": ind_qct,
            # Only if we have "query:data" - this field is for Beacon, which should have an access token:
            **({"matches": await filtered_qs.values_list("id", flat=True)} if perm_pheno_query_data else {}),
            "biosamples": {
                "count": tissues_count,
                "sampled_tissue": sampled_tissues,
            },
            **({
                "experiments": {
                    "count": experiments_count,
                    "experiment_type": experiment_types,
                }
            } if any(dt_perms_exp.values()) else {}),
        })
