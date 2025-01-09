import asyncio

from adrf.decorators import api_view
from bento_lib.responses import errors
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response

from chord_metadata_service.authz.helpers import get_data_type_query_permissions
from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAny
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.discovery.scope import get_request_discovery_scope
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
        - project (optional), dataset (optional): scope for search overview
    """

    # TODO: this probably shouldn't even exist as-is
    scope = await get_request_discovery_scope(request)

    individual_ids = request.GET.getlist("id") if request.method == "GET" else request.data.get("id", [])
    phenopackets = pheno_models.Phenopacket.get_model_scoped_queryset(scope).filter(subject_id__in=individual_ids)
    experiments = (
        experiments_models.Experiment
        .get_model_scoped_queryset(scope)
        .filter(biosample_id__in=[b async for b in phenopackets.values_list("biosamples__id", flat=True)])
    )

    # TODO: this hardcodes the biosample linked field set relationship
    #  - in general, this endpoint is less than ideal and should be derived from search results themselves vs. this
    #    hack-y mess of passing IDs around.

    # TODO: resource should be tied to search
    dt_permissions = await get_data_type_query_permissions(
        request, [DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT], scope.as_authz_resource()
    )

    authz_middleware.mark_authz_done(request)

    if not dt_permissions[DATA_TYPE_PHENOPACKET]["data"]:
        # If we don't have query:data on phenopackets, we cannot request a search overview
        return Response(errors.forbidden_error("Forbidden"), status=status.HTTP_403_FORBIDDEN)

    phenopackets_summary, experiments_summary = await asyncio.gather(
        dt_phenopacket_summary(scope, dt_permissions[DATA_TYPE_PHENOPACKET], phenopackets),
        dt_experiment_summary(scope, dt_permissions[DATA_TYPE_EXPERIMENT], experiments),
    )

    return Response({
        DATA_TYPE_PHENOPACKET: phenopackets_summary,
        DATA_TYPE_EXPERIMENT: experiments_summary,
    })
