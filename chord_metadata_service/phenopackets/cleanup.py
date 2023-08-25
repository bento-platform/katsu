import chord_metadata_service.experiments.models as em
import chord_metadata_service.phenopackets.models as pm

from chord_metadata_service.cleanup.remove import remove_items, remove_not_referenced
from chord_metadata_service.utils import build_id_set, build_id_set_from_model

__all__ = [
    "clean_meta_data",
    "clean_biosamples",
    "clean_phenotypic_features",
    "clean_procedures",
]


async def clean_meta_data() -> int:
    """
    Deletes orphan MetaData objects where the parent phenopacket has been deleted.
    TODO: This should be handled by a OneToOne relationship rather than this hack.
    """

    # Collect references to meta data
    meta_data_referenced = await build_id_set_from_model(pm.Phenopacket, "meta_data_id")

    # Remove metadata not referenced
    return await remove_not_referenced(pm.MetaData, meta_data_referenced, "metadata objects")


async def clean_biosamples() -> int:
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

    return await remove_not_referenced(pm.Biosample, biosamples_referenced, "biosamples")


async def clean_phenotypic_features() -> int:
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
    return await remove_items(pm.PhenotypicFeature, pf_to_remove, "phenotypic features")


async def clean_procedures() -> int:
    """
    Deletes all procedures which aren't pointed to by at least one biosample, since
    there is a many biosample -> one procedure style relationship currently (2023-01-19).
    """

    procedures_referenced = set()

    # Collect references to procedures in biosamples
    procedures_referenced |= await build_id_set_from_model(pm.Biosample, "procedure_id")

    return await remove_not_referenced(pm.Procedure, procedures_referenced, "procedures")
