import asyncio

from django.db.models import QuerySet

from chord_metadata_service.authz.types import DataPermissionsDict
from chord_metadata_service.discovery.censorship import thresholded_count
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.discovery.stats import queryset_stats_for_field
from chord_metadata_service.discovery.types import DiscoveryConfig
from chord_metadata_service.patients.summaries import individual_summary

from . import models

__all__ = [
    "biosample_summary",
    "disease_summary",
    "phenotypic_feature_summary",
    "dt_phenopacket_summary",
]


async def biosample_summary(
    phenopackets: QuerySet, discovery: DiscoveryConfig, phenopacket_permissions: DataPermissionsDict
):
    biosamples = models.Biosample.objects.filter(phenopacket__in=phenopackets)

    (
        biosamples_count,
        biosamples_taxonomy,
        biosamples_sampled_tissue,
        biosamples_histological_diagnosis,
        biosamples_is_control_sample,
    ) = await asyncio.gather(
        biosamples.acount(),
        queryset_stats_for_field(biosamples, "taxonomy__label", discovery, phenopacket_permissions),
        queryset_stats_for_field(biosamples, "sampled_tissue__label", discovery, phenopacket_permissions),
        queryset_stats_for_field(biosamples, "histological_diagnosis__label", discovery, phenopacket_permissions),
        queryset_stats_for_field(biosamples, "is_control_sample", discovery, phenopacket_permissions),
    )

    return {
        "count": thresholded_count(biosamples_count, discovery, phenopacket_permissions),
        "taxonomy": biosamples_taxonomy,
        "sampled_tissue": biosamples_sampled_tissue,
        "histological_diagnosis": biosamples_histological_diagnosis,
        "is_control_sample": biosamples_is_control_sample,
    }


async def disease_summary(
    phenopackets: QuerySet, discovery: DiscoveryConfig, phenopacket_permissions: DataPermissionsDict
):
    disease_stats = await queryset_stats_for_field(
        queryset=phenopackets,
        field="diseases__term__label",
        discovery=discovery,
        field_permissions=phenopacket_permissions,
    )
    return {
        # count is a number of unique disease terms (not all diseases in the database)
        "count": thresholded_count(len(disease_stats), discovery, phenopacket_permissions),
        "term": disease_stats,
    }


async def phenotypic_feature_summary(
    phenopackets: QuerySet, discovery: DiscoveryConfig, phenopacket_permissions: DataPermissionsDict
):
    # we don't need to re-filter by scope with stats_for_field for PhenotypicFeature, since the phenopackets have
    # already been filtered to the discovery scope.
    qs = models.PhenotypicFeature.objects.filter(phenopacket__in=phenopackets)
    phenotypic_features_count, phenotypic_features_type = await asyncio.gather(
        qs.distinct('pftype').acount(),
        queryset_stats_for_field(qs, "pftype__label", discovery, phenopacket_permissions),
    )
    return {
        # count is a number of unique phenotypic feature types, not all phenotypic features in the database.
        "count": thresholded_count(phenotypic_features_count, discovery, phenopacket_permissions),
        "type": phenotypic_features_type,
    }


async def dt_phenopacket_summary(
    scope: ValidatedDiscoveryScope, phenopacket_permissions: DataPermissionsDict, queryset: QuerySet | None = None
) -> dict:
    discovery = scope.discovery

    # Start with either all phenopackets or a subset specified by a parameter
    phenopackets = queryset if queryset is not None else models.Phenopacket.objects.all()

    # Apply scope to existing queryset to enforce it on the summarization
    if dataset_id := scope.dataset_id:
        phenopackets = phenopackets.filter(dataset_id=dataset_id)
    elif project_id := scope.project_id:
        # Project is set but dataset isn't
        phenopackets = phenopackets.select_related("dataset").filter(dataset__project_id=project_id)

    # Parallel-gather all statistics we may need for this response
    (
        phenopackets_count,
        biosample_summary_val,
        individual_summary_val,
        disease_summary_val,
        pf_summary_val,
    ) = await asyncio.gather(
        phenopackets.acount(),
        biosample_summary(phenopackets, discovery, phenopacket_permissions),
        individual_summary(phenopackets, discovery, phenopacket_permissions),
        disease_summary(phenopackets, discovery, phenopacket_permissions),
        phenotypic_feature_summary(phenopackets, discovery, phenopacket_permissions),
    )

    return {
        "count": thresholded_count(phenopackets_count, scope.discovery, phenopacket_permissions),
        "data_type_specific": {
            "biosamples": biosample_summary_val,
            "diseases": disease_summary_val,
            "individuals": individual_summary_val,
            "phenotypic_features": pf_summary_val,
        },
    }
