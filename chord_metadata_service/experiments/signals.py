import logging
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from chord_metadata_service.experiments.models import Experiment

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@receiver(pre_delete, sender=Experiment)
def cascade_delete_experiment_results(sender, instance, **kwargs):
    result = instance.experiment_results.all().delete()
    logging.info("cascade_delete_experiment_results", result)
