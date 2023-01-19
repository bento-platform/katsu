import chord_metadata_service.experiments.models as em
import chord_metadata_service.phenopackets.models as pm

from chord_metadata_service.logger import logger
from chord_metadata_service.utils import dict_first_val

__all__ = [
    "clean_biosamples",
    "clean_phenotypic_features",
    "clean_procedures",
]


def clean_biosamples() -> int:
    """
    Deletes all biosamples which aren't referenced anywhere in the application.
    Phenopackets and Experiments model tables should be deleted in the database
    BEFORE running this. Phenotypic features should be cleaned AFTER.
    """

    biosamples_referenced = set()

    # Collect references to biosamples in other data types
    biosamples_referenced.update(map(dict_first_val, pm.Phenopacket.objects.values("biosamples__id")))
    biosamples_referenced.update(map(dict_first_val, em.Experiment.objects.values("biosample_id")))
    # Explicitly don't check for phenotypic features here - they are attached to biosamples/phenopackets,
    #   and we want to delete them if the biosamples are otherwised not referenced elsewhere.

    # Remove null from set
    biosamples_referenced.discard(None)

    # Remove biosamples NOT in set
    biosamples_to_remove = set(
        map(dict_first_val, pm.Biosample.objects.exclude(id__in=biosamples_referenced).values("id")))
    n_to_remove = len(biosamples_to_remove)

    if n_to_remove:
        logger.info(f"Automatically cleaning up {n_to_remove} biosamples: {str(biosamples_to_remove)}")
        pm.Biosample.objects.filter(id__in=biosamples_to_remove).delete()
    else:
        logger.info("No biosamples set for auto-removal")

    return n_to_remove


def clean_phenotypic_features() -> int:
    """
    Deletes all phenotypic features without a biosample or phenopacket. This could
    happen especially in versions prior to 2.17.0, where on_delete was SET_NULL for both.
    Technically the schema still allows for phenotypic features that are not reference;
    however, for Bento's purposes, if this is called, we clean those up.
    """

    pf_to_remove_qs = pm.PhenotypicFeature.objects.filter(
        biosample__isnull=True,
        phenopacket__isnull=True,
    )

    pf_to_remove = set(map(dict_first_val, pf_to_remove_qs.values("id")))
    n_to_remove = len(pf_to_remove)

    if n_to_remove:
        logger.info(f"Automatically cleaning up {n_to_remove} phenotypic features: {str(pf_to_remove)}")
        pf_to_remove_qs.delete()
    else:
        logger.info("No phenotypic features set for auto-removal")

    return n_to_remove


def clean_procedures() -> int:
    """
    Deletes all procedures which aren't pointed to by at least one biosample, since
    there is a many biosample -> one procedure style relationship currently (2023-01-19).
    """

    procedures_referenced = set()

    # Collect references to procedures in biosamples
    procedures_referenced.update(map(dict_first_val, pm.Biosample.objects.values("procedure_id")))

    # Remove null from set
    procedures_referenced.discard(None)

    # Remove procedures NOT in set
    procedures_referenced = set(
        map(dict_first_val, pm.Procedure.objects.exclude(id__in=procedures_referenced).values("id")))
    n_to_remove = len(procedures_referenced)

    if n_to_remove:
        logger.info(f"Automatically cleaning up {n_to_remove} procedures: {str(procedures_referenced)}")
        pm.Procedure.objects.filter(id__in=procedures_referenced).delete()
    else:
        logger.info("No procedures set for auto-removal")

    return n_to_remove
