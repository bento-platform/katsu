import chord_metadata_service.chord.models as cm
import chord_metadata_service.phenopackets.models as pm


def clean_resources():
    # TODO
    cm.Dataset.objects.values("additional_resources__id")
    pm.MetaData.objects.values("resources__id")
