import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from chord_metadata_service.phenopackets.models import (
    Procedure,
    Biosample,
    PhenotypicFeature
)
from chord_metadata_service.phenopackets.indices import (
    build_procedure_index,
    remove_procedure_index,
    build_biosample_index,
    remove_biosample_index,
    build_phenotypicfeature_index,
    remove_phenotypicfeature_index
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@receiver(post_save, sender=Procedure)
def index_procedure(sender, instance, **kwargs):
    build_procedure_index(instance)
    logging.info(f'index_procedure_signal {instance.id}')


@receiver(post_delete, sender=Procedure)
def remove_procedure(sender, instance, **kwargs):
    remove_procedure_index(instance)
    logging.info(f'remove_procedure_signal {instance.id}')


@receiver(post_save, sender=Biosample)
def index_biosample(sender, instance, **kwargs):
    build_biosample_index(instance)
    logging.info(f'index_biosample_signal {instance.id}')


@receiver(post_delete, sender=Biosample)
def remove_biosample(sender, instance, **kwargs):
    remove_biosample_index(instance)
    logging.info(f'remove_biosample_signal {instance.id}')


@receiver(post_save, sender=PhenotypicFeature)
def index_phenotypicfeature(sender, instance, **kwargs):
    build_phenotypicfeature_index(instance)
    logging.info(f'index_phenotypicfeature_signal {instance.id}')


@receiver(post_delete, sender=PhenotypicFeature)
def remove_phenotypicfeature(sender, instance, **kwargs):
    remove_phenotypicfeature_index(instance)
    logging.info(f'remove_phenotypicfeature_signal {instance.id}')
