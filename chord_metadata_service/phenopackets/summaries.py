import asyncio

from django.db.models import QuerySet

from chord_metadata_service.restapi.utils import stats_for_field, queryset_stats_for_field
from . import models

__all__ = [
    "biosample_summary",
    "disease_summary",
    "phenotypic_feature_summary",
]


async def biosample_summary(phenopackets: QuerySet):
    biosamples = models.Biosample.objects.filter(phenopackets__in=phenopackets)

    (
        biosamples_count,
        biosamples_taxonomy,
        biosamples_sampled_tissue,
        biosamples_histological_diagnosis,
    ) = await asyncio.gather(
        biosamples.acount(),
        queryset_stats_for_field(biosamples, "taxonomy__label"),
        queryset_stats_for_field(biosamples, "sampled_tissue__label"),
        queryset_stats_for_field(biosamples, "histological_diagnosis__label"),
    )

    return {
        "count": biosamples_count,
        "taxonomy": biosamples_taxonomy,
        "sampled_tissue": biosamples_sampled_tissue,
        "histological_diagnosis": biosamples_histological_diagnosis,
    }


async def disease_summary(phenopackets: QuerySet):
    disease_stats = await queryset_stats_for_field(phenopackets, "diseases__term__label"),
    return {
        # count is a number of unique disease terms (not all diseases in the database)
        "count": len(disease_stats),
        "term": disease_stats,
    }


async def phenotypic_feature_summary(phenopackets: QuerySet):
    phenotypic_features_count, phenotypic_features_type = await asyncio.gather(
        models.PhenotypicFeature.objects.filter(phenopacket__in=phenopackets).distinct('pftype').acount(),
        stats_for_field(models.PhenotypicFeature, "pftype__label"),
    )
    return {
        # count is a number of unique phenotypic feature types, not all phenotypic features in the database.
        "count": phenotypic_features_count,
        "type": phenotypic_features_type,
    }
