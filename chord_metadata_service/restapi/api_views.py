import asyncio

from adrf.decorators import api_view
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response

from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.chord.permissions import OverrideOrSuperUserOnly
from chord_metadata_service.discovery.exceptions import DiscoveryConfigException
from chord_metadata_service.discovery.types import DiscoveryConfig
from chord_metadata_service.discovery.utils import get_request_discovery
from chord_metadata_service.experiments import models as experiments_models
from chord_metadata_service.experiments.summaries import dt_experiment_summary
from chord_metadata_service.metadata.service_info import get_service_info
from chord_metadata_service.phenopackets import models as pheno_models
from chord_metadata_service.phenopackets.summaries import dt_phenopacket_summary
from chord_metadata_service.restapi.models import SchemaType


OVERVIEW_AGE_BIN_SIZE = 10


@api_view()
@permission_classes([AllowAny])
async def service_info(_request: DrfRequest):
    """
    get:
    Return service info
    """

    return Response(await get_service_info())


async def build_overview_response(phenopackets: QuerySet, experiments: QuerySet, discovery: DiscoveryConfig):
    phenopackets_summary, experiments_summary = await asyncio.gather(
        dt_phenopacket_summary(phenopackets, discovery, low_counts_censored=False),
        dt_experiment_summary(experiments, discovery, low_counts_censored=False),
    )

    return Response({
        DATA_TYPE_PHENOPACKET: phenopackets_summary,
        DATA_TYPE_EXPERIMENT: experiments_summary,
    })


@extend_schema(
    description="Overview of all Phenopackets in the database",
    responses={
        200: inline_serializer(
            name='overview_response',
            fields={
                'phenopackets': serializers.IntegerField(),
                'data_type_specific': serializers.JSONField(),
            }
        )
    }
)
@api_view(["GET"])
@permission_classes([OverrideOrSuperUserOnly])
async def overview(request: DrfRequest):
    """
    get:
    Overview of all Phenopackets and experiments in the database - private endpoint
    """

    # TODO: permissions based on project - this endpoint should be scrapped / completely rethought
    try:
        discovery = await get_request_discovery(request)
    except DiscoveryConfigException as e:
        return Response(e.message, status=status.HTTP_404_NOT_FOUND)

    phenopackets = pheno_models.Phenopacket.objects.all()
    experiments = experiments_models.Experiment.objects.all()

    return await build_overview_response(phenopackets, experiments, discovery)


@api_view(["GET"])
@permission_classes([OverrideOrSuperUserOnly])
def extra_properties_schema_types(_request: DrfRequest):
    """
    get:
    Extra properties schema types
    """
    schema_types = dict(SchemaType.choices)
    return Response(schema_types)


@api_view(["GET", "POST"])
async def search_overview(request: DrfRequest):
    """
    get+post:
    Overview statistics of a list of patients (associated with a search result)
    - Parameter
        - id: a list of patient ids
    """

    # TODO: this should be project / dataset-scoped and probably shouldn't even exist as-is
    try:
        discovery = await get_request_discovery(request)
    except DiscoveryConfigException as e:
        return Response(e.message, status=status.HTTP_404_NOT_FOUND)

    individual_ids = request.GET.getlist("id") if request.method == "GET" else request.data.get("id", [])
    phenopackets = pheno_models.Phenopacket.objects.all().filter(subject_id__in=individual_ids)
    experiments = experiments_models.Experiment.objects.all().filter(
        biosample_id__in=phenopackets.values_list("biosamples__id", flat=True))

    # TODO: this hardcodes the biosample linked field set relationship
    #  - in general, this endpoint is less than ideal and should be derived from search results themselves vs. this
    #    hack-y mess of passing IDs around.

    return await build_overview_response(phenopackets, experiments, discovery)
