import asyncio

from django.db.models import QuerySet

from chord_metadata_service.discovery.censorship import thresholded_count
from chord_metadata_service.discovery.fields import get_age_numeric_binned
from chord_metadata_service.discovery.stats import queryset_stats_for_field
from . import models

__all__ = ["individual_summary"]


OVERVIEW_AGE_BIN_SIZE = 10  # TODO: configurable


async def individual_summary(phenopackets: QuerySet | None, low_counts_censored: bool):
    individuals = (
        models.Individual.objects.all()
        if phenopackets is None else models.Individual.objects.filter(phenopackets__in=phenopackets)
    )

    individual_count, individual_sex, individual_k_sex, individual_age, individual_taxonomy = await asyncio.gather(
        individuals.acount(),
        #  - Sex related fields stats are precomputed here and post processed later
        #    to include missing values inferred from the schema
        queryset_stats_for_field(individuals, "sex", low_counts_censored),
        queryset_stats_for_field(individuals, "karyotypic_sex", low_counts_censored),
        #  - Age
        get_age_numeric_binned(individuals, OVERVIEW_AGE_BIN_SIZE, low_counts_censored),
        #  - Taxonomy
        queryset_stats_for_field(individuals, "taxonomy__label", low_counts_censored),
    )

    return {
        "count": thresholded_count(individual_count, low_counts_censored),
        "sex": {k: individual_sex.get(k, 0) for k in (s[0] for s in models.Individual.SEX)},
        "karyotypic_sex": {k: individual_k_sex.get(k, 0) for k in (s[0] for s in models.Individual.KARYOTYPIC_SEX)},
        "age": individual_age,
        "taxonomy": individual_taxonomy,
    }
