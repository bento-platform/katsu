import chord_metadata_service.experiments.models as em
import chord_metadata_service.phenopackets.models as pm


def clean_biosamples():
    """
    Deletes all biosamples which aren't referenced anywhere in the application.
    Phenopackets and Experiments model tables should be deleted in the database
    BEFORE running this.
    """

    # TODO: do we need to handle null?

    biosamples_referenced = set()

    # TODO
    pm.Phenopacket.objects.values("biosamples__id")
    em.Experiment.objects.values("bisample_id")

    # TODO
    pass
