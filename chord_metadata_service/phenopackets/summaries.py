import asyncio

from django.db.models import QuerySet

from chord_metadata_service.discovery.censorship import thresholded_count
from chord_metadata_service.discovery.stats import stats_for_field, queryset_stats_for_field
from . import models

__all__ = [
    "biosample_summary",
    "disease_summary",
    "phenotypic_feature_summary",
    "dt_phenopacket_summary",
]

from chord_metadata_service.patients.summaries import individual_summary


async def biosample_summary(phenopackets: QuerySet, low_counts_censored: bool):
    biosamples = models.Biosample.objects.filter(phenopacket__in=phenopackets)

    (
        biosamples_count,
        biosamples_taxonomy,
        biosamples_sampled_tissue,
        biosamples_histological_diagnosis,
        biosamples_is_control_sample,
    ) = await asyncio.gather(
        biosamples.acount(),
        queryset_stats_for_field(biosamples, "taxonomy__label", low_counts_censored),
        queryset_stats_for_field(biosamples, "sampled_tissue__label", low_counts_censored),
        queryset_stats_for_field(biosamples, "histological_diagnosis__label", low_counts_censored),
        queryset_stats_for_field(biosamples, "is_control_sample", low_counts_censored),
    )

    return {
        "count": thresholded_count(biosamples_count, low_counts_censored),
        "taxonomy": biosamples_taxonomy,
        "sampled_tissue": biosamples_sampled_tissue,
        "histological_diagnosis": biosamples_histological_diagnosis,
        "is_control_sample": biosamples_is_control_sample,
    }


async def disease_summary(phenopackets: QuerySet, low_counts_censored: bool):
    disease_stats = await queryset_stats_for_field(phenopackets, "diseases__term__label", low_counts_censored)
    return {
        # count is a number of unique disease terms (not all diseases in the database)
        "count": thresholded_count(len(disease_stats), low_counts_censored),
        "term": disease_stats,
    }


async def phenotypic_feature_summary(phenopackets: QuerySet, low_counts_censored: bool):
    phenotypic_features_count, phenotypic_features_type = await asyncio.gather(
        models.PhenotypicFeature.objects.filter(phenopacket__in=phenopackets).distinct('pftype').acount(),
        stats_for_field(models.PhenotypicFeature, "pftype__label", low_counts_censored),
    )
    return {
        # count is a number of unique phenotypic feature types, not all phenotypic features in the database.
        "count": thresholded_count(phenotypic_features_count, low_counts_censored),
        "type": phenotypic_features_type,
    }


async def dt_phenopacket_summary(phenopackets: QuerySet, low_counts_censored: bool) -> dict:
    # Parallel-gather all statistics we may need for this response
    (
        phenopackets_count,
        biosample_summary_val,
        individual_summary_val,
        disease_summary_val,
        pf_summary_val,
    ) = await asyncio.gather(
        phenopackets.acount(),
        biosample_summary(phenopackets, low_counts_censored),
        individual_summary(phenopackets, low_counts_censored),
        disease_summary(phenopackets, low_counts_censored),
        phenotypic_feature_summary(phenopackets, low_counts_censored),
    )

    return {
        "count": thresholded_count(phenopackets_count, low_counts_censored),
        "data_type_specific": {
            "biosamples": biosample_summary_val,
            "diseases": disease_summary_val,
            "individuals": individual_summary_val,
            "phenotypic_features": pf_summary_val,
        },
    }
