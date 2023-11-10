import asyncio

from adrf.decorators import api_view
from bento_lib.auth.permissions import P_QUERY_DATA
from bento_lib.auth.resources import build_resource
from bento_lib.responses import errors
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from chord_metadata_service.authz.discovery import get_data_type_discovery_permissions
from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAny
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments import models as experiments_models, summaries as exp_summaries
from chord_metadata_service.experiments.summaries import dt_experiment_summary
from chord_metadata_service.metadata.service_info import SERVICE_INFO
from chord_metadata_service.patients import models as patients_models, summaries as patient_summaries
from chord_metadata_service.phenopackets import models as pheno_models, summaries as pheno_summaries
from chord_metadata_service.phenopackets.summaries import dt_phenopacket_summary
from chord_metadata_service.restapi.models import SchemaType

OVERVIEW_AGE_BIN_SIZE = 10


@api_view(["GET"])
@permission_classes([BentoAllowAny])
def service_info(_request: Request):
    """
    get:
    Return service info
    """

    return Response(SERVICE_INFO)


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
async def overview(request: Request):
    """
    get:
    Overview of all Phenopackets and experiments in the database
    """

    # TODO: permissions based on project - this endpoint should be scrapped / completely rethought

    # For now, this is on RESOURCE_EVERYTHING
    dt_permissions = await get_data_type_discovery_permissions(
        request, [DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT])

    # If we don't have AT LEAST one count permission, assume we're not supposed to see this page and return forbidden.
    if not any(dpd["counts"] or dpd["data"] for dpd in dt_permissions.values()):
        authz_middleware.mark_authz_done(request)
        return Response(errors.forbidden_error(), status=status.HTTP_403_FORBIDDEN)

    phenopackets = pheno_models.Phenopacket.objects.all()
    experiments = experiments_models.Experiment.objects.all()

    phenopackets_summary, experiments_summary = await asyncio.gather(
        dt_phenopacket_summary(phenopackets, dt_permissions),
        dt_experiment_summary(experiments, dt_permissions),
    )

    return Response({
        DATA_TYPE_PHENOPACKET: phenopackets_summary,
        DATA_TYPE_EXPERIMENT: experiments_summary,
    })


@api_view(["GET"])
@permission_classes([BentoAllowAny])
def extra_properties_schema_types(_request: Request):
    """
    get:
    Extra properties schema types
    """
    schema_types = dict(SchemaType.choices)
    return Response(schema_types)


@api_view(["GET", "POST"])
async def search_overview(request: Request):
    """
    get+post:
    Overview statistics of a list of patients (associated with a search result)
    - Parameter
        - id: a list of patient ids
    """

    # TODO: this should be project / dataset-scoped and probably shouldn't even exist as-is

    individual_ids = request.GET.getlist("id") if request.method == "GET" else request.data.get("id", [])

    queryset = patients_models.Individual.objects.all().filter(id__in=individual_ids)

    datasets_accessed = frozenset({ds_id async for ds_id in (
        queryset
        .exclude(phenopackets__dataset_id__isnull=True)
        .values_list("phenopackets__dataset__project__identifier", "phenopackets__dataset__identifier")
    )})

    # IMPORTANT PERMISSIONS NOTE: ----–----–----–----–----–----–----–----–----–----–------------------------------------
    # Even though we're basically just accessing counts here, we require the query:data permissions since otherwise
    # users could discover the ID format/which IDs exist in the instance (BAD!!!)
    # ------------------------------------------------------------------------------------------------------------------

    authz_resources = tuple(build_resource(project=d[0], dataset=d[1]) for d in datasets_accessed)
    auth_res = await authz_middleware.async_evaluate(request, authz_resources, (P_QUERY_DATA,))
    allowed_datasets = tuple(r["dataset"] for r, p in zip(authz_resources, auth_res) if p[0])

    authorized_individuals = queryset.filter(phenopackets__dataset_id__in=allowed_datasets)
    # We need to select these separately, since we could be authorized to access one phenopacket for an individual
    # but not another - thus we get just phenopackets we're authorized to get for individuals we selected:
    authorized_phenopackets = pheno_models.Phenopacket.objects.filter(
        subject__in=authorized_individuals, dataset_id__in=allowed_datasets)

    # TODO: this hardcodes the biosample linked field set relationship
    #  - in general, this endpoint is less than ideal and should be derived from search results themselves vs. this
    #    hack-y mess of passing IDs around.
    authorized_experiments = experiments_models.Experiment.objects.filter(
        dataset_id__in=allowed_datasets,
        biosample_id__in=authorized_phenopackets.values_list("biosample_id", flat=True),
    )

    # We have the "query:data" permission on all datasets we get back here for all data types.
    # No low-count thresholding is needed.

    biosample_summary, disease_summary, individual_summary, pf_summary, experiment_summary = await asyncio.gather(
        pheno_summaries.biosample_summary(authorized_phenopackets, low_counts_censored=False),
        pheno_summaries.disease_summary(authorized_phenopackets, low_counts_censored=False),
        patient_summaries.individual_summary(authorized_phenopackets, low_counts_censored=False),
        pheno_summaries.phenotypic_feature_summary(authorized_phenopackets, low_counts_censored=False),
        exp_summaries.experiment_summary(authorized_experiments, low_counts_censored=False),
    )

    return Response({
        "biosamples": biosample_summary,
        "diseases": disease_summary,
        "individuals": individual_summary,
        "phenotypic_features": pf_summary,
        "experiments": experiment_summary,
    })
