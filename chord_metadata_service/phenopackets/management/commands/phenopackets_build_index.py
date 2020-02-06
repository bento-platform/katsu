import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from chord_metadata_service.phenopackets.models import (
    Procedure,
    Biosample,
    PhenotypicFeature
)
from chord_metadata_service.phenopackets.indices import (
    build_procedure_index,
    build_biosample_index,
    build_phenotypicfeature_index
)
from chord_metadata_service.metadata.elastic import es


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = """
        Takes every phenopacket-related data in the DB, port them over 
        to FHIR-compliant JSON and upload them into elasticsearch
    """
    def handle(self, *args, **options):
        # TODO: currently only place we create the index, will have to review
        if es:
            es.indices.create(index=settings.FHIR_INDEX_NAME, ignore=400)

            procedures = Procedure.objects.all()

            for procedure in procedures:
                created_or_updated = build_procedure_index(procedure)
                logger.info(f"{created_or_updated} index for procedure ID {procedure.id}")

            biosamples = Biosample.objects.all()

            for biosample in biosamples:
                created_or_updated = build_biosample_index(biosample)
                logger.info(f"{created_or_updated} index for biosample ID {biosample.id}")

            features = PhenotypicFeature.objects.all()

            for feature in features:
                created_or_updated = build_phenotypicfeature_index(feature)
                logger.info(f"{created_or_updated} index for phenotypic feature ID {feature.id}")
        else:
            logger.error("No connection to elasticsearch")
