import chord_metadata_service.experiments.models as em
import chord_metadata_service.phenopackets.models as pm

from structlog.stdlib import BoundLogger

from chord_metadata_service.cleanup.remove import remove_items, remove_not_referenced
from chord_metadata_service.utils import build_id_set, build_id_set_from_model

__all__ = [
    "clean_meta_data",
    "clean_biosamples",
    "clean_phenotypic_features",
    "clean_interpretations",
    "clean_diagnoses",
    "clean_genomic_interpretations",
    "clean_variant_interpretations",
]


async def clean_meta_data(logger: BoundLogger) -> int:
    """
    Deletes orphan MetaData objects where the parent phenopacket has been deleted.
    TODO: This should be handled by a OneToOne relationship rather than this hack.
    """

    # Collect references to meta data
    meta_data_referenced = await build_id_set_from_model(pm.Phenopacket, "meta_data_id")

    # Remove metadata not referenced
    return await remove_not_referenced(pm.MetaData, meta_data_referenced, "metadata objects", logger)


async def clean_biosamples(logger: BoundLogger) -> int:
    """
    Deletes all biosamples which aren't referenced anywhere in the application.
    Phenopackets and Experiments model tables should be deleted in the database
    BEFORE running this. Phenotypic features should be cleaned AFTER.
    """

    biosamples_referenced = set()

    # Collect references to biosamples in other data types
    biosamples_referenced |= await build_id_set_from_model(pm.Phenopacket, "biosamples__id")
    biosamples_referenced |= await build_id_set_from_model(em.Experiment, "biosample_id")
    # Explicitly don't check for phenotypic features here - they are attached to biosamples/phenopackets,
    #   and we want to delete them if the biosamples are otherwised not referenced elsewhere.

    return await remove_not_referenced(pm.Biosample, biosamples_referenced, "biosamples", logger)


async def clean_phenotypic_features(logger: BoundLogger) -> int:
    """
    Deletes all phenotypic features without a biosample or phenopacket. This could
    happen especially in versions prior to 2.17.0, where on_delete was SET_NULL for both.
    Technically the schema still allows for phenotypic features that are not reference;
    however, for Bento's purposes, if this is called, we clean those up.
    """

    # We can skip some steps and collect only those not used directly here.

    pf_to_remove = await build_id_set(
        qs=pm.PhenotypicFeature.objects.filter(
            biosample__isnull=True,
            phenopacket__isnull=True,
        ),
        field="id",
    )
    return await remove_items(pm.PhenotypicFeature, pf_to_remove, "phenotypic features", logger)


async def clean_interpretations(logger: BoundLogger) -> int:
    interpretations_referenced = await build_id_set_from_model(pm.Phenopacket, "interpretations__id")
    return await remove_not_referenced(
        pm.Interpretation, interpretations_referenced, "interpretations", logger
    )


async def clean_diagnoses(logger: BoundLogger) -> int:
    diagnoses_referenced = await build_id_set_from_model(pm.Interpretation, "diagnosis__id")
    return await remove_not_referenced(pm.Diagnosis, diagnoses_referenced, "diagnosis", logger)


async def clean_genomic_interpretations(logger: BoundLogger) -> int:
    gi_referenced = await build_id_set_from_model(pm.Diagnosis, "genomic_interpretations__id")
    return await remove_not_referenced(
        pm.GenomicInterpretation, gi_referenced, "genomic interpretations", logger
    )


async def clean_variant_interpretations(logger: BoundLogger) -> int:
    vis_referenced = await build_id_set_from_model(pm.GenomicInterpretation, "variant_interpretation")
    return await remove_not_referenced(
        pm.VariantInterpretation, vis_referenced, "variant interpretations", logger
    )
