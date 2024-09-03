import asyncio

from adrf.decorators import api_view
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import permission_classes
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response

from chord_metadata_service.authz.helpers import get_data_type_query_permissions
from chord_metadata_service.authz.permissions import BentoAllowAny, OverrideOrSuperUserOnly
from chord_metadata_service.authz.types import DataTypeDiscoveryPermissions
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.discovery.types import DiscoveryConfig
from chord_metadata_service.discovery.utils import ValidatedDiscoveryScope
from chord_metadata_service.experiments import models as experiments_models
from chord_metadata_service.experiments.summaries import dt_experiment_summary
from chord_metadata_service.metadata.service_info import get_service_info
from chord_metadata_service.phenopackets import models as pheno_models
from chord_metadata_service.phenopackets.summaries import dt_phenopacket_summary
from chord_metadata_service.restapi.models import SchemaType


OVERVIEW_AGE_BIN_SIZE = 10


@api_view()
@permission_classes([BentoAllowAny])
async def service_info(_request: DrfRequest):
    """
    get:
    Return service info
    """

    return Response(await get_service_info())


async def build_overview_response(
    phenopackets: QuerySet,
    experiments: QuerySet,
    discovery: DiscoveryConfig,
    dt_permissions: DataTypeDiscoveryPermissions,
):
    phenopackets_summary, experiments_summary = await asyncio.gather(
        dt_phenopacket_summary(phenopackets, discovery, dt_permissions[DATA_TYPE_PHENOPACKET]),
        dt_experiment_summary(experiments, discovery, dt_permissions[DATA_TYPE_EXPERIMENT]),
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
    # use node level discovery config for private overview
    discovery_scope = ValidatedDiscoveryScope(project=None, dataset=None)
    discovery = await discovery_scope.get_discovery()

    phenopackets = pheno_models.Phenopacket.objects.all()
    experiments = experiments_models.Experiment.objects.all()

    dt_permissions = await get_data_type_query_permissions(
        request, [DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT], discovery_scope.as_authz_resource()
    )

    return await build_overview_response(phenopackets, experiments, discovery, dt_permissions)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
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
    # use node level discovery config for private search overview
    discovery_scope = ValidatedDiscoveryScope(project=None, dataset=None)
    discovery = await discovery_scope.get_discovery()

    individual_ids = request.GET.getlist("id") if request.method == "GET" else request.data.get("id", [])
    phenopackets = pheno_models.Phenopacket.objects.all().filter(subject_id__in=individual_ids)
    experiments = experiments_models.Experiment.objects.all().filter(
        biosample_id__in=phenopackets.values_list("biosamples__id", flat=True))

    # TODO: this hardcodes the biosample linked field set relationship
    #  - in general, this endpoint is less than ideal and should be derived from search results themselves vs. this
    #    hack-y mess of passing IDs around.

    # TODO: resource should be tied to search
    dt_permissions = await get_data_type_query_permissions(
        request, [DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT], discovery_scope.as_authz_resource()
    )

    return await build_overview_response(phenopackets, experiments, discovery, dt_permissions)
