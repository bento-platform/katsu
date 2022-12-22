import chord_metadata_service.mcode.models as mm
import chord_metadata_service.phenopackets.models as pm


def clean_individuals():
    """
    Deletes all individuals which aren't referenced anywhere in the application.
    Phenopackets/biosamples should be cleaned BEFORE running this.
    """

    # TODO: do we need to handle null?

    individuals_referenced = set()

    # TODO
    mm.LabsVital.objects.values("individual_id")
    mm.MCodePacket.objects.values("individual_id")

    # TODO
    pm.Biosample.objects.values("individual_id")
    pm.Phenopacket.objects.values("subject_id")

    # TODO
