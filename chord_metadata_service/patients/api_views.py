import asyncio

from adrf.views import APIView
from asgiref.sync import async_to_sync
from bento_lib.auth.permissions import Permission, P_QUERY_DATA
from bento_lib.responses import errors
from bento_lib.search import build_search_response
from datetime import datetime
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.exceptions import ValidationError
from django.db.models import Count, F, Q
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import filters, serializers, status
from rest_framework.decorators import action
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from rest_framework.settings import api_settings

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.viewset import BentoAuthzScopedModelViewSet, BentoAuthzScopedModelGenericListViewSet
from chord_metadata_service.chord import data_types as dts
from chord_metadata_service.discovery import responses as dres
from chord_metadata_service.discovery.censorship import get_threshold, thresholded_count
from chord_metadata_service.discovery.exceptions import DiscoveryScopeException, DiscoveryEmptyException
from chord_metadata_service.discovery.filtering import discovery_filter_queryset
from chord_metadata_service.discovery.pydantic_models import DiscoveryQuery
from chord_metadata_service.discovery.scope import get_request_discovery_scope
from chord_metadata_service.discovery.stats import individual_biosample_tissue_stats, individual_experiment_type_stats
from chord_metadata_service.discovery.utils import get_discovery_data_type_permissions
from chord_metadata_service.logger import logger
from chord_metadata_service.phenopackets.api_views import (
    BIOSAMPLE_PREFETCH, BIOSAMPLE_SELECT_REL, PHENOPACKET_PREFETCH, PHENOPACKET_SELECT_REL
)
from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.phenopackets.serializers import PhenopacketSerializer
from chord_metadata_service.restapi.api_renderers import (
    PhenopacketsRenderer,
    IndividualCSVRenderer,
    IndividualBentoSearchRenderer,
)
from chord_metadata_service.restapi.constants import MODEL_ID_PATTERN
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination, BatchResultsSetPagination
from chord_metadata_service.restapi.negociation import FormatInPostContentNegotiation
from chord_metadata_service.restapi.utils import (
    build_experiments_by_subject,
    get_biosamples_with_experiment_details,
    response_optionally_as_attachment,
)

from .filters import IndividualFilter
from .models import Individual
from .serializers import IndividualSerializer

OUTPUT_FORMAT_BENTO_SEARCH_RESULT = "bento_search_result"


class IndividualViewSet(BentoAuthzScopedModelViewSet):
    """
    get:
    Return a list of all existing individuals

    post:
    Create a new individual

    """

    serializer_class = IndividualSerializer
    pagination_class = LargeResultsSetPagination
    renderer_classes = (
        *api_settings.DEFAULT_RENDERER_CLASSES,
        PhenopacketsRenderer,
        IndividualCSVRenderer,
        IndividualBentoSearchRenderer,
    )
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = IndividualFilter
    ordering_fields = ["id"]
    search_fields = ["sex"]
    lookup_value_regex = MODEL_ID_PATTERN

    data_type = dts.DATA_TYPE_PHENOPACKET

    def permission_from_request(self, request: DrfRequest) -> Permission | None:
        if self.action == "phenopackets":
            # GET or POST; either way, we're querying data for this action
            return P_QUERY_DATA
        return super().permission_from_request(request)

    @async_to_sync
    async def get_queryset(self):
        scope = await get_request_discovery_scope(self.request)
        return (
            Individual.get_model_scoped_queryset(scope)
            .prefetch_related(
                *(f"biosamples__{p}" for p in BIOSAMPLE_PREFETCH),
                *(f"phenopackets__{p}" for p in PHENOPACKET_PREFETCH if p != "subject"),
            )
            .order_by("id")
        )

    def list(self, request, *args, **kwargs):
        if request.query_params.get("format") == OUTPUT_FORMAT_BENTO_SEARCH_RESULT:
            # TODO: this whole thing is badly-placed: it really should be an alternate view of phenopackets, not
            #  individuals. As such, it can return >1 record for the same individual if they have >1 phenopacket.

            scope = async_to_sync(get_request_discovery_scope)(self.request)

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
            biosamples_experiments_details = get_biosamples_with_experiment_details(individual_ids)
            qs = (
                Phenopacket
                .get_model_scoped_queryset(scope)
                .prefetch_related("dataset__project")
                .filter(subject__id__in=individual_ids)
                .values(
                    "subject_id",
                    "dataset_id",
                    phenopacket_id=F("id"),
                    project_id=F("dataset__project_id"),
                    alternate_ids=Coalesce(F("subject__alternate_ids"), [])
                )
                .annotate(
                    num_experiments=Count("biosamples__experiments"),
                    biosamples=Coalesce(
                        ArrayAgg("biosamples__id", distinct=True, filter=Q(biosamples__id__isnull=False)),
                        []
                    )
                )
            )
            experiments_with_biosamples = build_experiments_by_subject(biosamples_experiments_details)
            results = [
                {
                    **data,
                    "experiments_with_biosamples": experiments_with_biosamples.get(data["subject_id"], [])
                }
                for data in qs
            ]
            return Response(build_search_response(results, start))

        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["GET", "POST"])
    def phenopackets(self, request: DrfRequest, *_args, **_kwargs):
        scope = async_to_sync(get_request_discovery_scope)(request)

        individual = self.get_object()

        phenopackets = (
            Phenopacket.get_model_scoped_queryset(scope)
            .filter(subject=individual)
            .prefetch_related(*PHENOPACKET_PREFETCH)
            .select_related(*PHENOPACKET_SELECT_REL)
            .annotate(project=F("dataset__project_id"))
            .order_by("id")
        )

        return response_optionally_as_attachment(
            request,
            PhenopacketSerializer(phenopackets, many=True).data,
            f"{individual.id}_phenopackets.json"
        )


class IndividualBatchViewSet(BentoAuthzScopedModelGenericListViewSet):

    serializer_class = IndividualSerializer
    pagination_class = BatchResultsSetPagination
    renderer_classes = (
        *api_settings.DEFAULT_RENDERER_CLASSES,
        PhenopacketsRenderer,
        IndividualCSVRenderer,
        IndividualBentoSearchRenderer,
    )
    # Override to infer the renderer based on a `format` argument from the POST request body
    content_negotiation_class = FormatInPostContentNegotiation

    data_type = dts.DATA_TYPE_PHENOPACKET

    @async_to_sync
    async def get_queryset(self):
        scope = await get_request_discovery_scope(self.request)

        individual_ids = self.request.data.get("id", None)
        filter_by_id = {"id__in": individual_ids} if individual_ids else {}
        queryset = (
            Individual
            .get_model_scoped_queryset(scope)
            .prefetch_related(
                *(f"biosamples__{p}" for p in BIOSAMPLE_PREFETCH),
                *(f"biosamples__{p}" for p in BIOSAMPLE_SELECT_REL),
                *(f"phenopackets__{p}" for p in PHENOPACKET_PREFETCH),
                *(f"phenopackets__{p}" for p in PHENOPACKET_SELECT_REL),
            )
            .select_related("vital_status")
            .filter(**filter_by_id)
            .order_by("id")
        )

        return queryset


# noinspection PyMethodMayBeStatic
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

    async def get(self, request, *_args, **_kwargs):
        try:
            discovery_scope = await get_request_discovery_scope(request)
        except DiscoveryScopeException as e:
            authz_middleware.mark_authz_done(request)
            return Response(e.message, status=status.HTTP_404_NOT_FOUND)

        dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)
        dt_perms_pheno = dt_permissions[dts.DATA_TYPE_PHENOPACKET]
        dt_perms_exp = dt_permissions[dts.DATA_TYPE_EXPERIMENT]

        # We can't respond if we don't have at least phenopackets counts permission
        if not dt_perms_pheno.counts:
            authz_middleware.mark_authz_done(request)
            return Response(errors.forbidden_error(), status=status.HTTP_403_FORBIDDEN)

        discovery = discovery_scope.discovery

        perm_pheno_query_data = dt_perms_pheno.data

        # Get individuals filtered to the requested scope
        base_qs = Individual.get_model_scoped_queryset(discovery_scope)

        query = DiscoveryQuery.from_drf_request(request)
        queried_fields = query.queried_filter_fields()

        try:
            filtered_qs = (
                await discovery_filter_queryset(
                    discovery_scope, query, "individual", base_qs, dt_permissions, logger
                )
            )[0]
        except DiscoveryEmptyException:
            authz_middleware.mark_authz_done(request)
            return Response(dres.NO_PUBLIC_DATA_AVAILABLE, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            await logger.ainfo(
                "discovery individuals endpoint recieved validation error", exc=e, scope_repr=repr(discovery_scope)
            )
            authz_middleware.mark_authz_done(request)
            return Response(errors.bad_request_error(
                *(e.error_list if hasattr(e, "error_list") else e.error_dict.items()),
            ), status=status.HTTP_400_BAD_REQUEST)

        ind_qct = thresholded_count(await filtered_qs.acount(), discovery, dt_perms_pheno)
        threshold = get_threshold(discovery, dt_perms_pheno)

        # structured event logging for public search: embed search details
        await logger.ainfo(
            "public individuals search",
            queried_fields=queried_fields,
            individual_count=ind_qct,
            threshold=threshold,
            sub_threshold=ind_qct <= threshold,
        )

        if ind_qct == 0 and not perm_pheno_query_data:
            # 0 count means insufficient data if we only have counts permissions, but means a true 0 if we have full
            # data permissions.
            authz_middleware.mark_authz_done(request)
            return Response(dres.INSUFFICIENT_DATA_AVAILABLE)

        # filtered_qs: filtered Individual queryset
        filtered_qs = filtered_qs.annotate(
            phenopacket_id=F("phenopackets__id"),
            dataset_id=F("phenopackets__dataset__identifier"),
            project_id=F("phenopackets__dataset__project__identifier"),
        )

        (tissues_count, sampled_tissues), (experiments_count, experiment_types) = await asyncio.gather(
            individual_biosample_tissue_stats(filtered_qs, discovery, dt_perms_pheno),
            individual_experiment_type_stats(filtered_qs, discovery, dt_perms_exp),
        )

        authz_middleware.mark_authz_done(request)
        return Response({
            "count": ind_qct,
            # Only if we have "query:data" - this field is for Beacon, which should have an access token:
            **(
                {
                    "matches": filtered_qs.values_list("id", flat=True),
                    # Below is a temporary detailed match list so we can start building a better search UI.
                    "matches_detail": [
                        {
                            "id": i.id,
                            **({
                                "phenopacket_id": i.phenopacket_id,
                                "project_id": i.project_id,
                                "dataset_id": i.dataset_id,
                            } if i.phenopacket_id else {
                                "phenopacket_id": None,
                                "project_id": None,
                                "dataset_id": None,
                            })
                        } async for i in filtered_qs
                    ],
                }
                if perm_pheno_query_data
                else {}
            ),
            "biosamples": {
                "count": tissues_count,
                "sampled_tissue": sampled_tissues.model_dump(mode="json"),
            },
            **({
                "experiments": {
                    "count": experiments_count,
                    "experiment_type": experiment_types.model_dump(mode="json"),
                }
            } if dt_perms_exp.any_permissions() else {}),
        })
