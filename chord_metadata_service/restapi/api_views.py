import asyncio

from adrf.decorators import api_view
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response

from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.chord.permissions import OverrideOrSuperUserOnly
from chord_metadata_service.experiments import models as experiments_models, summaries as exp_summaries
from chord_metadata_service.experiments.summaries import dt_experiment_summary
from chord_metadata_service.metadata.service_info import get_service_info
from chord_metadata_service.patients import summaries as patient_summaries
from chord_metadata_service.phenopackets import models as pheno_models, summaries as pheno_summaries
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
async def overview(_request: DrfRequest):
    """
    get:
    Overview of all Phenopackets and experiments in the database - private endpoint
    """

    # TODO: permissions based on project - this endpoint should be scrapped / completely rethought

    phenopackets = pheno_models.Phenopacket.objects.all()
    experiments = experiments_models.Experiment.objects.all()

    phenopackets_summary, experiments_summary = await asyncio.gather(
        dt_phenopacket_summary(phenopackets, low_counts_censored=False),
        dt_experiment_summary(experiments, low_counts_censored=False),
    )

    return Response({
        DATA_TYPE_PHENOPACKET: phenopackets_summary,
        DATA_TYPE_EXPERIMENT: experiments_summary,
    })


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

    individual_ids = request.GET.getlist("id") if request.method == "GET" else request.data.get("id", [])
    phenopackets = pheno_models.Phenopacket.objects.all().filter(subject_id__in=individual_ids)
    experiments = experiments_models.Experiment.objects.all().filter(
        biosample_id__in=phenopackets.values_list("biosamples__id", flat=True))

    # TODO: this hardcodes the biosample linked field set relationship
    #  - in general, this endpoint is less than ideal and should be derived from search results themselves vs. this
    #    hack-y mess of passing IDs around.

    # We have the "query:data" permission on all datasets we get back here for all data types.
    # No low-count thresholding is needed.

    biosample_summary, disease_summary, individual_summary, pf_summary, experiment_summary = await asyncio.gather(
        pheno_summaries.biosample_summary(phenopackets, low_counts_censored=False),
        pheno_summaries.disease_summary(phenopackets, low_counts_censored=False),
        patient_summaries.individual_summary(phenopackets, low_counts_censored=False),
        pheno_summaries.phenotypic_feature_summary(phenopackets, low_counts_censored=False),
        exp_summaries.experiment_summary(experiments, low_counts_censored=False),
    )

    return Response({
        "biosamples": biosample_summary,
        "diseases": disease_summary,
        "individuals": individual_summary,
        "phenotypic_features": pf_summary,
        "experiments": experiment_summary,
    })
